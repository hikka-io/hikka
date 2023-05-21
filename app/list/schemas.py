from datetime import datetime
from typing import Union

from app.schemas import (
    PaginationResponse,
    WatchStatusEnum,
    AnimeResponse,
    ORJSONModel,
)


# Args
class WatchFilterArgs(ORJSONModel):
    status: Union[WatchStatusEnum, None] = None


# Responses
class WatchResponse(ORJSONModel):
    note: Union[str, None]
    anime: AnimeResponse
    updated: datetime
    created: datetime
    reference: str
    episodes: int
    status: str
    score: int


class AnimeFavouriteResponse(ORJSONModel):
    anime: AnimeResponse
    created: datetime
    reference: str


class WatchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[WatchResponse]


class AnimeFavouritePaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[AnimeFavouriteResponse]
