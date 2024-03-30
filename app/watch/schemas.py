from pydantic import field_validator
from pydantic import Field
from app import constants
from enum import Enum

from app.schemas import (
    AnimeSearchArgsBase,
    PaginationResponse,
    WatchResponseBase,
    AnimeResponse,
    UserResponse,
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
    note: str | None = Field(default=None, max_length=2048, examples=["🤯"])
    episodes: int = Field(default=0, ge=0, le=10000, examples=[3])
    rewatches: int = Field(default=0, ge=0, le=100, examples=[2])
    score: int = Field(default=0, ge=0, le=10, examples=[8])
    status: WatchStatusEnum


class AnimeWatchSearchArgs(AnimeSearchArgsBase):
    sort: list[str] = ["watch_score:desc", "watch_created:desc"]
    watch_status: WatchStatusEnum | None = None

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        valid_orders = ["asc", "desc"]
        valid_fields = [
            "watch_episodes",
            "watch_created",
            "watch_score",
            "media_type",
            "start_date",
            "scored_by",
            "score",
        ]

        if len(sort_list) != len(set(sort_list)):
            raise ValueError("Invalid sort: duplicates")

        for sort_item in sort_list:
            parts = sort_item.split(":")

            if len(parts) != 2:
                raise ValueError(f"Invalid sort format: {sort_item}")

            field, order = parts

            if field not in valid_fields or order not in valid_orders:
                raise ValueError(f"Invalid sort value: {sort_item}")

        return sort_list


# Responses
class WatchResponse(WatchResponseBase):
    anime: AnimeResponse


class UserResponseWithWatch(UserResponse):
    watch: list[WatchResponseBase]


class WatchPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[WatchResponse]


class UserWatchPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[UserResponseWithWatch]


class WatchStatsResponse(CustomModel):
    duration: int = Field(examples=[24])
    completed: int = Field(examples=[20])
    watching: int = Field(examples=[3])
    planned: int = Field(examples=[7])
    dropped: int = Field(examples=[1])
    on_hold: int = Field(examples=[2])
