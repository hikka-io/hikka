from pydantic import BaseModel, Field
from ..utils import Datetime
from typing import Union

class WatchResponse(BaseModel):
    note: Union[str, None]
    created: Datetime
    updated: Datetime
    user_score: int
    reference: str
    episodes: int
    status: str

class WatchDeleteResponse(BaseModel):
    success: bool
