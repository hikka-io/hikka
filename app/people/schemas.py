from app.schemas import (
    PaginationResponse,
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


class PersonSearchPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[PersonResponse]


class PersonAnimePaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[PersonAnimeResponse]
