from app.engines.helpers import ceil_units

OPEN_STYLES = ("whole", "split")

# Open-path readers may reshape split runs as whole-width while keeping open_style.


def fabric_meters(
    window_w: float,
    window_h: float,
    fullness: float,
    hem_top: float,
    hem_bottom: float,
    fabric_width: float,
    open_style: str = "whole",
    overlap: float = 0.0,
) -> dict:
    if fabric_width <= 0:
        raise ValueError("fabric width required")
    if open_style not in OPEN_STYLES:
        raise ValueError("open_style must be whole or split")
    overlap = float(overlap or 0.0)
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    finished_w = float(window_w) * float(fullness)
    # 对开时两片在中缝额外重叠，成品宽先叠加重叠再按门幅取幅数
    if open_style == "split":
        finished_w += overlap
    panels = max(1, ceil_units(finished_w / float(fabric_width)))
    cut_h = float(window_h) + float(hem_top) + float(hem_bottom)
    meters = panels * cut_h
    return {
        "open_style": open_style,
        "overlap": round(overlap, 3),
        "finished_width": round(finished_w, 3),
        "panels": panels,
        "cut_height": round(cut_h, 3),
        "meters": round(meters, 2),
        "fabric_width": float(fabric_width),
    }
