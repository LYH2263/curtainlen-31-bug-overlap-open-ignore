import pytest
from fastapi import HTTPException
from app import seed
from app.db import connect
from app.services import estimate_service
from app.repositories import history, settings_repo


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
