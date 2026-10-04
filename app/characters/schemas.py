from app.common.schemas.anime import AnimeResponseWithWatch
from app.common.schemas.manga import MangaResponseWithRead
from app.common.schemas.novel import NovelResponseWithRead
from app.common.schemas.character import CharacterResponse
from app.common.schemas.person import PersonResponse
from pydantic import Field

from app.schemas import (
    PaginationResponse,
    CustomModel,
)


# Responses
class CharacterFullResponse(CharacterResponse):
    description_ua: str | None = Field(examples=["..."])


class CharacterCountResponse(CharacterFullResponse, CustomModel):
    comments_count: int
    voices_count: int
    anime_count: int
    manga_count: int
    novel_count: int


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
