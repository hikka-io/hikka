from pydantic import Field

from app.schemas import (
    PaginationResponse,
    CharacterResponse,
    PersonResponse,
    AnimeResponse,
    CustomModel,
)


# Responses
class CharacterVoiceResponse(CustomModel):
    person: PersonResponse
    anime: AnimeResponse
    language: str


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


class CharacterVoicesPaginationResponse(CustomModel):
    list: list[CharacterVoiceResponse]
    pagination: PaginationResponse
