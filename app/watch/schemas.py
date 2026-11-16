from app.common.schemas.anime import AnimeSearchArgsBase
from app.common.schemas.watch import WatchResponseBase
from app.common.schemas.watch import WatchStatusEnum
from app.common.schemas.anime import AnimeResponse
from app.common.schemas.user import UserResponse
from pydantic import field_validator
from pydantic import model_validator
from app.utils import check_sort
from pydantic import Field
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    UnixTimestamp,
    CustomModel,
)


# Enums
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
    start_date: UnixTimestamp | None = None
    end_date: UnixTimestamp | None = None
    status: WatchStatusEnum

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date is not None and self.end_date is not None:
            if self.start_date > self.end_date:
                raise ValueError("Hello there time traveler")

        return self


class AnimeWatchSearchArgs(AnimeSearchArgsBase):
    sort: list[str] = ["watch_score:desc", "watch_created:desc"]
    watch_status: WatchStatusEnum | None = None

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        return check_sort(
            sort_list,
            [
                "native_score",
                "native_scored_by",
                "watch_episodes",
                "watch_updated",
                "watch_created",
                "watch_score",
                "media_type",
                "start_date",
                "scored_by",
                "score",
            ],
        )


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
