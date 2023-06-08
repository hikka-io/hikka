from pydantic import Field

from app.schemas import (
    PaginationResponse,
    PersonResponse,
    AnimeResponse,
    ORJSONModel,
)


# Responses
class PersonAnimeResponse(ORJSONModel):
    role: str = Field(example="Producer")
    anime: AnimeResponse


class PersonSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[PersonResponse]


class PersonAnimePaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[PersonAnimeResponse]
