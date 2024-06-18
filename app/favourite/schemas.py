from app.schemas import datetime_pd
from pydantic import Field
from app import constants
from enum import Enum

from app.schemas import (
    AnimeResponseWithWatch,
    MangaResponseWithRead,
    NovelResponseWithRead,
    PaginationResponse,
    CollectionResponse,
    CharacterResponse,
    CustomModel,
)


# Enums
class FavouriteContentTypeEnum(str, Enum):
    content_collection = constants.CONTENT_COLLECTION
    content_character = constants.CONTENT_CHARACTER
    content_anime = constants.CONTENT_ANIME
    content_manga = constants.CONTENT_MANGA
    content_novel = constants.CONTENT_NOVEL


# Mixins
class FavouriteMeta(CustomModel):
    favourite_created: datetime_pd


# Responses
class FavouriteResponse(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    created: datetime_pd = Field(examples=[1686088809])


class FavouriteAnimeResponse(AnimeResponseWithWatch, FavouriteMeta):
    pass


class FavouriteMangaResponse(MangaResponseWithRead, FavouriteMeta):
    pass


class FavouriteNovelResponse(NovelResponseWithRead, FavouriteMeta):
    pass


class FavouriteCollectionResponse(CollectionResponse, FavouriteMeta):
    pass


class FavouriteCharacterResponse(CharacterResponse, FavouriteMeta):
    pass


class FavouritePaginationResponse(CustomModel):
    list: list[
        FavouriteAnimeResponse
        | FavouriteMangaResponse
        | FavouriteNovelResponse
        | FavouriteCollectionResponse
        | FavouriteCharacterResponse
    ]
    pagination: PaginationResponse
