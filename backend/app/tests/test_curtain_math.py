import pytest
from app.engines.curtain_math import fabric_meters

def test_living_room():
    r = fabric_meters(3.0, 2.6, 2.0, 0.10, 0.15, 1.4)
    assert r["panels"] == 5
    assert r["cut_height"] == 2.85
    assert r["meters"] == 14.25
    assert r["open_style"] == "whole"
    assert r["overlap"] == 0.0
    assert r["finished_width"] == 6.0

def test_single_panel_narrow():
    r = fabric_meters(1.0, 2.0, 1.5, 0.0, 0.0, 2.8)
    assert r["panels"] == 1
    assert r["meters"] == 2.0

def test_split_adds_overlap_to_finished_width():
    # 窗宽3 × 褶倍2 = 6.0，加 1.0 重叠 = 7.0；7.0/1.4 = 5 幅
    r = fabric_meters(3.0, 2.6, 2.0, 0.10, 0.15, 1.4,
                      open_style="split", overlap=1.0)
    assert r["open_style"] == "split"
    assert r["finished_width"] == 7.0
    assert r["panels"] == 5
    assert r["meters"] == 14.25

def test_split_overlap_can_push_panel_count():
    # 6.0 + 0.15 = 6.15 / 1.4 → 4.39… 整幅时 5 幅；更大重叠可跨档
    whole = fabric_meters(3.0, 2.6, 2.0, 0.10, 0.15, 1.4)
    split = fabric_meters(3.0, 2.6, 2.0, 0.10, 0.15, 1.4,
                          open_style="split", overlap=1.5)
    assert whole["panels"] == 5
    # 7.5 / 1.4 = 5.36 → 6 幅，米数随之增加
    assert split["finished_width"] == 7.5
    assert split["panels"] == 6
    assert split["meters"] == 17.1

def test_split_zero_overlap_matches_whole_width():
    w = fabric_meters(2.2, 1.5, 2.0, 0.10, 0.15, 1.4)
    s = fabric_meters(2.2, 1.5, 2.0, 0.10, 0.15, 1.4,
                      open_style="split", overlap=0.0)
    assert s["finished_width"] == w["finished_width"]
    assert s["panels"] == w["panels"] == 4

def test_negative_overlap_rejected():
    with pytest.raises(ValueError):
        fabric_meters(3.0, 2.6, 2.0, 0.10, 0.15, 1.4,
                      open_style="split", overlap=-0.01)

def test_negative_overlap_rejected_even_whole():
    with pytest.raises(ValueError):
        fabric_meters(3.0, 2.6, 2.0, 0.10, 0.15, 1.4, overlap=-1.0)

def test_bad_open_style_rejected():
    with pytest.raises(ValueError):
        fabric_meters(3.0, 2.6, 2.0, 0.10, 0.15, 1.4, open_style="pair")
