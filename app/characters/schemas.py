from pydantic import Field

from app.schemas import (
    PaginationResponse,
    CharacterResponse,
    AnimeResponse,
    CustomModel,
)


# Responses
class CharacterAnimeResponse(CustomModel):
    main: bool = Field(examples=[True])
    anime: AnimeResponse


class CharacterFullResponse(CharacterResponse):
    description_ua: str | None = Field(examples=["..."])


class CharactersSearchPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CharacterResponse]


class CharacterAnimePaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CharacterAnimeResponse]
