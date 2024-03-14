from app.schemas import (
    PaginationResponse,
    CharacterResponse,
    PersonResponse,
    AnimeResponse,
    CustomModel,
)


# Responses
class AnimeStaffRoleResponse(CustomModel):
    name_en: str | None
    name_ua: str | None


class PersonAnimeResponse(CustomModel):
    roles: list[AnimeStaffRoleResponse]
    anime: AnimeResponse


class PersonCharactersResponse(CustomModel):
    character: CharacterResponse
    anime: AnimeResponse
    language: str


class PersonSearchPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[PersonResponse]


class PersonAnimePaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[PersonAnimeResponse]


class PersonCharactersPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[PersonCharactersResponse]
