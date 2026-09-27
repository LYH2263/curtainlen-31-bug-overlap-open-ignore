from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.repositories import settings_repo
import math
router = APIRouter()

class SettingBody(BaseModel):
    key: str
    value: str

# 数值型设置：必须能解析为非负数
_NUMERIC_NONNEGATIVE = ("default_fullness", "default_overlap")

@router.get("/settings")
def settings(): return settings_repo.get_all()

@router.put("/settings")
def put_setting(body: SettingBody):
    # 只允许调默认褶倍/默认重叠，避免任意键污染
    if body.key not in ("default_fullness", "default_overlap"):
        raise HTTPException(422, "unknown setting key")
    if body.key in _NUMERIC_NONNEGATIVE:
        try:
            v = float(body.value)
        except (TypeError, ValueError):
            raise HTTPException(422, f"{body.key} must be a number")
        if not math.isfinite(v) or v < 0:
            raise HTTPException(422, f"{body.key} must be a finite number >= 0")
    settings_repo.upsert(body.key, body.value)
    return settings_repo.get_all()
