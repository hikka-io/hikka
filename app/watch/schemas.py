from datetime import datetime
from pydantic import Field
from app import constants
from typing import Union
from enum import Enum

from app.schemas import (
    PaginationResponse,
    AnimeResponse,
    ORJSONModel,
)


# Enums
class WatchStatusEnum(str, Enum):
    completed = constants.WATCH_COMPLETED
    watching = constants.WATCH_WATCHING
    planned = constants.WATCH_PLANNED
    on_hold = constants.WATCH_ON_HOLD
    dropped = constants.WATCH_DROPPED


# Args
class WatchArgs(ORJSONModel):
    note: Union[str, None] = Field(default=None, max_length=140, example="🤯")
    score: int = Field(default=0, ge=0, le=10, example=8)
    episodes: int = Field(default=0, ge=0, example=3)
    status: WatchStatusEnum


class WatchFilterArgs(ORJSONModel):
    status: Union[WatchStatusEnum, None] = None


# Responses
class WatchResponse(ORJSONModel):
    reference: str = Field(example="c773d0bf-1c42-4c18-aec8-1bdd8cb0a434")
    updated: datetime = Field(example=1686088809)
    created: datetime = Field(example=1686088809)
    note: Union[str, None] = Field(example="🤯")
    status: str = Field(example="watching")
    episodes: int = Field(example=3)
    score: int = Field(example=8)
    anime: AnimeResponse


class WatchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[WatchResponse]


class WatchStatsResponse(ORJSONModel):
    completed: int = Field(example=20)
    watching: int = Field(example=3)
    planned: int = Field(example=7)
    dropped: int = Field(example=1)
    on_hold: int = Field(example=2)
