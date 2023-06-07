from pydantic import Field
from typing import Union

from app.schemas import (
    AnimeFavouriteResponse,
    PaginationResponse,
    WatchStatusEnum,
    WatchResponse,
    ORJSONModel,
)


# Args
class WatchFilterArgs(ORJSONModel):
    status: Union[WatchStatusEnum, None] = None


# Responses
class WatchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[WatchResponse]


class AnimeFavouritePaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[AnimeFavouriteResponse]


class WatchStatsResponse(ORJSONModel):
    completed: int = Field(example=20)
    watching: int = Field(example=3)
    planned: int = Field(example=7)
    dropped: int = Field(example=1)
    on_hold: int = Field(example=2)
