from typing import Union

from app.schemas import (
    PaginationResponse,
    CharacterResponse,
    AnimeResponse,
    ORJSONModel,
)


# Responses
class CharacterAnimeResponse(ORJSONModel):
    anime: AnimeResponse
    main: bool


class CharactersSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[CharacterResponse]


class CharacterAnimePaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[CharacterAnimeResponse]
