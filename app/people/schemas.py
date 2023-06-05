from typing import Union

from app.schemas import (
    PaginationResponse,
    AnimeResponse,
    ORJSONModel,
)


# Responses
class PersonResponse(ORJSONModel):
    name_native: Union[str, None]
    name_ua: Union[str, None]
    name_en: Union[str, None]
    image: Union[str, None]
    slug: str


class PersonAnimeResponse(ORJSONModel):
    anime: AnimeResponse
    role: str


class PersonSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[PersonResponse]


class PersonAnimePaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[PersonAnimeResponse]
