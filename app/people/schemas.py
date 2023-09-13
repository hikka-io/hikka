from pydantic import Field
from typing import Union

from app.schemas import (
    PaginationResponse,
    PersonResponse,
    AnimeResponse,
    ORJSONModel,
)


# Responses
class AnimeStaffRoleResponse(ORJSONModel):
    name_en: Union[str, None]
    name_ua: Union[str, None]


class PersonAnimeResponse(ORJSONModel):
    roles: list[AnimeStaffRoleResponse]
    anime: AnimeResponse


class PersonSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[PersonResponse]


class PersonAnimePaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[PersonAnimeResponse]
