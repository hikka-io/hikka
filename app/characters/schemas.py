from typing import Union

from app.schemas import (
    PaginationResponse,
    AnimeResponse,
    ORJSONModel,
)


# Responses
class CharacterResponse(ORJSONModel):
    name_ua: Union[str, None]
    name_en: Union[str, None]
    name_ja: Union[str, None]
    image: Union[str, None]
    slug: str


class CharacterAnimeResponse(ORJSONModel):
    anime: AnimeResponse
    main: bool


class CharactersSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[CharacterResponse]


class CharacterAnimePaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[CharacterAnimeResponse]
