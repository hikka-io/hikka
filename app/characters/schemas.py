from pydantic import Field

from app.schemas import (
    PaginationResponse,
    CharacterResponse,
    AnimeResponse,
    ORJSONModel,
)


# Responses
class CharacterAnimeResponse(ORJSONModel):
    main: bool = Field(example=True)
    anime: AnimeResponse


class CharactersSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[CharacterResponse]


class CharacterAnimePaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[CharacterAnimeResponse]
