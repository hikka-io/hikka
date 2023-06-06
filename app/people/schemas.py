from typing import Union

from app.schemas import (
    PaginationResponse,
    PersonResponse,
    AnimeResponse,
    ORJSONModel,
)


# Responses
class PersonAnimeResponse(ORJSONModel):
    anime: AnimeResponse
    role: str


class PersonSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[PersonResponse]


class PersonAnimePaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[PersonAnimeResponse]
