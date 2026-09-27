import pytest
from fastapi import HTTPException
from app import seed
from app.db import connect
from app.services import estimate_service
from app.repositories import history, settings_repo
from app.routers.settings import SettingBody, put_setting


@pytest.fixture()
def db(tmp_path, monkeypatch):
    import app.db as dbmod
    monkeypatch.setattr(dbmod, "DB_PATH", tmp_path / "t.db")
    seed.init_db()
    return tmp_path / "t.db"


def _run_count():
    c = connect()
    try:
        return c.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]
    finally:
        c.close()


def test_negative_overlap_422_and_no_row(db):
    before = _run_count()
    with pytest.raises(HTTPException) as ei:
        estimate_service.run_estimate(1, 1, save=True, note="",
                                      open_style="split", overlap=-0.05)
    assert ei.value.status_code == 422
    # 校验失败：预览不给结果，保存也不在 calc_runs 加行
    assert _run_count() == before


def test_whole_finished_width_unchanged(db):
    r = estimate_service.run_estimate(1, 1, save=False, note="", open_style="whole")
    # 3.0 × 2.0 = 6.0，与改造前一致，不叠加重叠
    assert r["finished_width"] == 6.0
    assert r["panels"] == 5
    assert r["open_style"] == "whole"


def test_split_uses_default_overlap_when_omitted(db):
    r = estimate_service.run_estimate(1, 1, save=False, note="", open_style="split")
    # seed 默认 0.10
    assert r["overlap"] == 0.1
    assert r["finished_width"] == 6.1


def test_saved_run_freezes_style_and_overlap(db):
    saved = estimate_service.run_estimate(1, 1, save=True, note="",
                                          open_style="split", overlap=0.25)
    rid = saved["run_id"]
    assert rid
    expected = {
        "open_style": "split",
        "overlap": 0.25,
        "finished_width": saved["finished_width"],
        "meters": saved["meters"],
        "panels": saved["panels"],
    }
    # 事后改掉系统默认重叠
    settings_repo.upsert("default_overlap", "0.9")
    got = history.get_run(rid)["result"]
    for k, v in expected.items():
        assert got[k] == v
    # 新测算才用新默认值
    fresh = estimate_service.run_estimate(1, 1, save=False, note="", open_style="split")
    assert fresh["overlap"] == 0.9
    # 按编号打开仍是当初的开合方式
    assert history.get_run(rid)["result"]["open_style"] == "split"


def test_get_missing_run_is_none(db):
    assert history.get_run(9999) is None


def test_list_and_detail_match_saved_snapshot(db):
    saved = estimate_service.run_estimate(1, 1, save=True, note="",
                                          open_style="split", overlap=0.25)
    rid = saved["run_id"]
    keys = ("open_style", "overlap", "finished_width", "panels", "cut_height", "meters")
    detail = history.get_run(rid)["result"]
    row = next(r for r in history.list_runs() if r["id"] == rid)["result"]
    for k in keys:
        assert detail[k] == saved[k]
        assert row[k] == saved[k]


def test_snapshot_does_not_drift_after_master_data_changes(db):
    saved = estimate_service.run_estimate(1, 1, save=True, note="",
                                          open_style="split", overlap=0.25)
    rid = saved["run_id"]
    # 事后改窗宽与门幅：旧编号必须钉住写入时的成品宽 / panels / 米数
    c = connect()
    try:
        c.execute("UPDATE windows SET width=9.9 WHERE id=1")
        c.execute("UPDATE fabrics SET fabric_width=0.5 WHERE id=1")
        c.commit()
    finally:
        c.close()
    got = history.get_run(rid)["result"]
    for k in ("open_style", "overlap", "finished_width", "panels", "cut_height", "meters"):
        assert got[k] == saved[k]


def test_negative_default_overlap_setting_rejected(db):
    with pytest.raises(HTTPException) as ei:
        put_setting(SettingBody(key="default_overlap", value="-0.1"))
    assert ei.value.status_code == 422
    assert settings_repo.get_all().get("default_overlap") == "0.10"
