from fastapi import APIRouter
from pydantic import BaseModel
from app.repositories import settings_repo
router = APIRouter()

class SettingBody(BaseModel):
    key: str
    value: str

@router.get("/settings")
def settings(): return settings_repo.get_all()

@router.put("/settings")
def put_setting(body: SettingBody):
    # 只允许调默认褶倍/默认重叠，避免任意键污染
    if body.key not in ("default_fullness", "default_overlap"):
        from fastapi import HTTPException
        raise HTTPException(422, "unknown setting key")
    settings_repo.upsert(body.key, body.value)
    return settings_repo.get_all()
