from pydantic import Field

from app.schemas import (
    PaginationResponse,
    CharacterResponse,
    AnimeResponse,
    CustomModel,
)


# Responses
class CharacterAnimeResponse(CustomModel):
    main: bool = Field(example=True)
    anime: AnimeResponse


class CharactersSearchPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CharacterResponse]


class CharacterAnimePaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CharacterAnimeResponse]
