from app.schemas import (
    PaginationResponse,
    PersonResponse,
    AnimeResponse,
    ORJSONModel,
)


# Responses
class AnimeStaffRoleResponse(ORJSONModel):
    name_en: str | None
    name_ua: str | None


class PersonAnimeResponse(ORJSONModel):
    roles: list[AnimeStaffRoleResponse]
    anime: AnimeResponse


class PersonSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[PersonResponse]


class PersonAnimePaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[PersonAnimeResponse]
