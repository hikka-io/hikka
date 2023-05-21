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
