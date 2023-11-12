from datetime import datetime
from pydantic import Field
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    AnimeResponse,
    CustomModel,
)


# Enums
class WatchStatusEnum(str, Enum):
    completed = constants.WATCH_COMPLETED
    watching = constants.WATCH_WATCHING
    planned = constants.WATCH_PLANNED
    on_hold = constants.WATCH_ON_HOLD
    dropped = constants.WATCH_DROPPED


# Args
class WatchArgs(CustomModel):
    note: str | None = Field(default=None, max_length=140, example="🤯")
    score: int = Field(default=0, ge=0, le=10, example=8)
    episodes: int = Field(default=0, ge=0, example=3)
    status: WatchStatusEnum


class WatchFilterArgs(CustomModel):
    status: WatchStatusEnum | None = None


# Responses
class WatchResponse(CustomModel):
    reference: str = Field(example="c773d0bf-1c42-4c18-aec8-1bdd8cb0a434")
    updated: datetime = Field(example=1686088809)
    created: datetime = Field(example=1686088809)
    status: str = Field(example="watching")
    note: str | None = Field(example="🤯")
    episodes: int = Field(example=3)
    score: int = Field(example=8)
    anime: AnimeResponse


class WatchPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[WatchResponse]


class WatchStatsResponse(CustomModel):
    completed: int = Field(example=20)
    watching: int = Field(example=3)
    planned: int = Field(example=7)
    dropped: int = Field(example=1)
    on_hold: int = Field(example=2)
