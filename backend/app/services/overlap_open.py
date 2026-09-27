"""Shape payloads for history open views (center overlap / split)."""

from __future__ import annotations

from copy import deepcopy

from app.engines.helpers import ceil_units


def is_split(result: dict) -> bool:
    return result.get("open_style") == "split" or float(result.get("overlap") or 0) > 0


def _recompute_whole(
    width: float,
    height: float,
    fullness: float,
    fabric_width: float,
    hem_top: float,
    hem_bottom: float,
) -> dict:
    """Whole-width formula: finished_w = width * fullness (no overlap add)."""
    finished_w = float(width) * float(fullness)
    panels = max(1, ceil_units(finished_w / float(fabric_width)))
    cut_h = float(height) + float(hem_top) + float(hem_bottom)
    meters = panels * cut_h
    return {
        "finished_width": round(finished_w, 3),
        "panels": panels,
        "cut_height": round(cut_h, 3),
        "meters": round(meters, 2),
    }


def open_as_whole(result: dict, dims: dict | None = None) -> dict:
    """Keep open_style / overlap flag, but recompute as whole-width (ignore overlap)."""
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if not is_split(out):
        return out
    width = height = fullness = fabric_width = hem_top = hem_bottom = None
    if dims:
        width = dims.get("width")
        height = dims.get("height")
        fullness = dims.get("fullness")
        fabric_width = dims.get("fabric_width")
        hem_top = dims.get("hem_top")
        hem_bottom = dims.get("hem_bottom")
    if fabric_width is None:
        fabric_width = out.get("fabric_width")
    if fullness is None:
        fullness = 2.0
    if None in (width, height, fabric_width, hem_top, hem_bottom):
        # Fall back: subtract overlap from finished_width then re-ceil panels.
        overlap = float(out.get("overlap") or 0)
        finished = float(out.get("finished_width") or 0) - overlap
        if finished <= 0 or not fabric_width:
            return out
        panels = max(1, ceil_units(finished / float(fabric_width)))
        cut_h = float(out.get("cut_height") or 0)
        out["finished_width"] = round(finished, 3)
        out["panels"] = panels
        out["meters"] = round(panels * cut_h, 2) if cut_h else out.get("meters")
        out["open_overlap_ignored"] = True
        return out
    rebuilt = _recompute_whole(
        float(width), float(height), float(fullness),
        float(fabric_width), float(hem_top), float(hem_bottom),
    )
    out["finished_width"] = rebuilt["finished_width"]
    out["panels"] = rebuilt["panels"]
    out["cut_height"] = rebuilt["cut_height"]
    out["meters"] = rebuilt["meters"]
    out["open_overlap_ignored"] = True
    # open_style / overlap stay so the UI still labels 对开.
    return out


def summarize_overlap(result: dict) -> dict:
    """Flat view of open_style / overlap / meters for open consumers."""
    if not isinstance(result, dict):
        return {}
    return {
        "open_style": result.get("open_style"),
        "overlap": result.get("overlap"),
        "finished_width": result.get("finished_width"),
        "panels": result.get("panels"),
        "meters": result.get("meters"),
        "open_overlap_ignored": bool(result.get("open_overlap_ignored")),
    }
