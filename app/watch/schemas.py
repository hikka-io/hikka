from app.constants import WATCH, WATCH_PLANNED
from pydantic import BaseModel, Field
from app.utils import Datetime
from typing import Union


# Args
class WatchArgs(BaseModel):
    status: str = Field(default=WATCH_PLANNED, regex="|".join(WATCH))
    user_score: int = Field(default=1, ge=1, le=10)
    episodes: int = Field(default=0, ge=0)
    note: Union[str, None] = None


# Responses
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
