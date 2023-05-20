from app.constants import WATCH, WATCH_PLANNED
from app.schemas import ORJSONModel
from datetime import datetime
from pydantic import Field
from typing import Union


# Args
class WatchArgs(ORJSONModel):
    status: str = Field(default=WATCH_PLANNED, regex="|".join(WATCH))
    score: int = Field(default=1, ge=1, le=10)
    episodes: int = Field(default=0, ge=0)
    note: Union[str, None] = None


# Responses
class WatchResponse(ORJSONModel):
    note: Union[str, None]
    created: datetime
    updated: datetime
    score: int
    reference: str
    episodes: int
    status: str


class WatchDeleteResponse(ORJSONModel):
    success: bool
