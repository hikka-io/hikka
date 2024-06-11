from pydantic import Field

from app.schemas import (
    AnimeResponseWithWatch,
    MangaResponseWithRead,
    NovelResponseWithRead,
    PaginationResponse,
    CharacterResponse,
    PersonResponse,
    CustomModel,
)


# Responses
class CharacterFullResponse(CharacterResponse):
    description_ua: str | None = Field(examples=["..."])


class CharacterCountResponse(CharacterFullResponse, CustomModel):
    voices_count: int
    anime_count: int


class CharacterVoiceResponse(CustomModel):
    anime: AnimeResponseWithWatch
    person: PersonResponse
    language: str


class CharacterAnimeResponse(CustomModel):
    main: bool = Field(examples=[True])
    anime: AnimeResponseWithWatch


class CharacterMangaResponse(CustomModel):
    main: bool = Field(examples=[True])
    manga: MangaResponseWithRead


class CharacterNovelResponse(CustomModel):
    main: bool = Field(examples=[True])
    novel: NovelResponseWithRead


class CharactersSearchPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CharacterResponse]


class CharacterAnimePaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CharacterAnimeResponse]


class CharacterMangaPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CharacterMangaResponse]


class CharacterNovelPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CharacterNovelResponse]


class CharacterVoicesPaginationResponse(CustomModel):
    list: list[CharacterVoiceResponse]
    pagination: PaginationResponse
