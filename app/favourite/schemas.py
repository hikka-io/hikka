from datetime import datetime
from pydantic import Field
from app import constants
from enum import Enum

from app.collections.schemas import CollectionResponse

from app.schemas import (
    AnimeResponseWithWatch,
    PaginationResponse,
    CharacterResponse,
    CustomModel,
)


# Enums
class ContentTypeEnum(str, Enum):
    content_collection = constants.CONTENT_COLLECTION
    content_character = constants.CONTENT_CHARACTER
    content_anime = constants.CONTENT_ANIME


# Mixins
class FavouriteMeta(CustomModel):
    favourite_created: datetime


# Responses
class FavouriteResponse(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    created: datetime = Field(examples=[1686088809])


class FavouriteAnimeResponse(AnimeResponseWithWatch, FavouriteMeta):
    pass


class FavouriteCollectionResponse(CollectionResponse, FavouriteMeta):
    pass


class FavouriteCharacterResponse(CharacterResponse, FavouriteMeta):
    pass


class FavouritePaginationResponse(CustomModel):
    list: list[
        FavouriteAnimeResponse
        | FavouriteCollectionResponse
        | FavouriteCharacterResponse
    ]
    pagination: PaginationResponse


# ToDo: remove me
class FavouriteResponseContentLegacy(FavouriteResponse):
    anime: AnimeResponseWithWatch


# ToDo: remove me
class FavouritePaginationResponseLegacy(CustomModel):
    list: list[FavouriteResponseContentLegacy]
    pagination: PaginationResponse
