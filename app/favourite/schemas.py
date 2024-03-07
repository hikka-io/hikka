from datetime import datetime
from pydantic import Field
from app import constants
from enum import Enum

from app.schemas import (
    AnimeResponseWithWatch,
    PaginationResponse,
    CustomModel,
)


# Enums
class ContentTypeEnum(str, Enum):
    content_anime = constants.CONTENT_ANIME


# Responses
class AnimeFavouriteResponseWithWatch(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    created: datetime = Field(examples=[1686088809])
    anime: AnimeResponseWithWatch


class AnimeFavouritePaginationResponse(CustomModel):
    list: list[AnimeFavouriteResponseWithWatch]
    pagination: PaginationResponse
