from pydantic import Field
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    WatchResponseBase,
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


class WatchOrderEnum(str, Enum):
    media_type = constants.WATCH_ORDER_MEDIA_TYPE
    episodes = constants.WATCH_ORDER_EPISODES
    score = constants.WATCH_ORDER_SCORE


class WatchSortEnum(str, Enum):
    desc = constants.SORT_DESC
    asc = constants.SORT_ASC


# Args
class WatchArgs(CustomModel):
    note: str | None = Field(default=None, max_length=1024, examples=["🤯"])
    episodes: int = Field(default=0, ge=0, le=10000, examples=[3])
    score: int = Field(default=0, ge=0, le=10, examples=[8])
    status: WatchStatusEnum


class WatchFilterArgs(CustomModel):
    status: WatchStatusEnum | None = None
    order: WatchOrderEnum = Field(default=constants.WATCH_ORDER_SCORE)
    sort: WatchSortEnum = Field(default=constants.SORT_DESC)


# Responses
class WatchResponse(WatchResponseBase):
    anime: AnimeResponse


class WatchPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[WatchResponse]


class WatchStatsResponse(CustomModel):
    completed: int = Field(examples=[20])
    watching: int = Field(examples=[3])
    planned: int = Field(examples=[7])
    dropped: int = Field(examples=[1])
    on_hold: int = Field(examples=[2])
