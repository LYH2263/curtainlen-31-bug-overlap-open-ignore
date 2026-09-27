from typing import Literal, Optional
from pydantic import BaseModel

class EstimateRequest(BaseModel):
    window_id: int
    fabric_id: int
    save: bool = False
    note: str = ""
    open_style: Literal["whole", "split"] = "whole"
    overlap: Optional[float] = None
