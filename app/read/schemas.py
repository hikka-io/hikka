from app.schemas import CustomModel, UserResponse
from pydantic import Field, field_validator
from app.schemas import PaginationResponse
from pydantic import model_validator
from app.utils import check_sort
from app import constants
from enum import Enum

from app.schemas import (
    MangaSearchBaseMixin,
    ReadResponseBase,
    MangaResponse,
    NovelResponse,
    UnixTimestamp,
    YearsMixin,
)


# Enums
class ReadStatusEnum(str, Enum):
    completed = constants.READ_COMPLETED
    reading = constants.READ_READING
    on_hold = constants.READ_ON_HOLD
    dropped = constants.READ_DROPPED
    planned = constants.READ_PLANNED


class ReadContentTypeEnum(str, Enum):
    content_manga = constants.CONTENT_MANGA
    content_novel = constants.CONTENT_NOVEL


# Args
class ReadArgs(CustomModel):
    note: str | None = Field(default=None, max_length=2048, examples=["🤯"])
    chapters: int = Field(default=0, ge=0, le=10000, examples=[3])
    volumes: int = Field(default=0, ge=0, le=10000, examples=[3])
    rereads: int = Field(default=0, ge=0, le=100, examples=[2])
    score: int = Field(default=0, ge=0, le=10, examples=[8])
    start_date: UnixTimestamp | None = None
    end_date: UnixTimestamp | None = None
    status: ReadStatusEnum

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date is not None and self.end_date is not None:
            if self.start_date > self.end_date:
                raise ValueError("Hello there time traveler")

        return self


class ReadSearchArgs(CustomModel, MangaSearchBaseMixin, YearsMixin):
    sort: list[str] = ["read_score:desc", "read_created:desc"]
    read_status: ReadStatusEnum | None = None

    @field_validator("sort")
    def validate_sort(cls, sort_list):
        return check_sort(
            sort_list,
            [
                "read_chapters",
                "read_volumes",
                "read_updated",
                "read_created",
                "read_score",
                "media_type",
                "start_date",
                "scored_by",
                "score",
            ],
        )


# Responses
class ReadResponse(ReadResponseBase):
    content: MangaResponse | NovelResponse


class UserResponseWithRead(UserResponse):
    read: list[ReadResponseBase]


class UserReadPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[UserResponseWithRead]


class ReadStatsResponse(CustomModel):
    completed: int = Field(examples=[20])
    reading: int = Field(examples=[3])
    planned: int = Field(examples=[7])
    dropped: int = Field(examples=[1])
    on_hold: int = Field(examples=[2])


class ReadPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[ReadResponse]
