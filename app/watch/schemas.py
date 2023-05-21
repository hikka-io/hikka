from app.schemas import ORJSONModel, WatchStatusEnum
from datetime import datetime
from pydantic import Field
from typing import Union


# Args
class WatchArgs(ORJSONModel):
    score: int = Field(default=1, ge=1, le=10)
    episodes: int = Field(default=0, ge=0)
    note: Union[str, None] = None
    status: WatchStatusEnum


# Responses
class WatchResponse(ORJSONModel):
    note: Union[str, None]
    created: datetime
    updated: datetime
    reference: str
    episodes: int
    status: str
    score: int


class WatchDeleteResponse(ORJSONModel):
    success: bool
