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
class PersonCountResponse(PersonResponse, CustomModel):
    characters_count: int
    anime_count: int


class RoleResponse(CustomModel):
    name_en: str | None
    name_ua: str | None


class PersonAnimeResponse(CustomModel):
    roles: list[RoleResponse]
    anime: AnimeResponseWithWatch


class PersonMangaResponse(CustomModel):
    roles: list[RoleResponse]
    manga: MangaResponseWithRead


class PersonNovelResponse(CustomModel):
    roles: list[RoleResponse]
    novel: NovelResponseWithRead


class PersonCharactersResponse(CustomModel):
    character: CharacterResponse
    anime: AnimeResponseWithWatch
    language: str


class PersonSearchPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[PersonResponse]


class PersonAnimePaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[PersonAnimeResponse]


class PersonMangaPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[PersonMangaResponse]


class PersonNovelPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[PersonNovelResponse]


class PersonCharactersPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[PersonCharactersResponse]
