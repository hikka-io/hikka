from pydantic import constr
from pydantic import Field
from app import constants
from typing import Union
from enum import Enum

from app.schemas import (
    PaginationResponse,
    AnimeResponse,
    ORJSONModel,
)


# Enums
class CompanyAnimeTypeEnum(str, Enum):
    producer = constants.COMPANY_ANIME_PRODUCER
    studio = constants.COMPANY_ANIME_STUDIO


# Args
class CompaniesSearchArgs(ORJSONModel):
    query: Union[constr(min_length=3, max_length=255), None] = None
    page: int = Field(default=1, gt=0)


class ComapnyAnimeArgs(ORJSONModel):
    type: Union[CompanyAnimeTypeEnum, None] = None
    page: int = Field(default=1, gt=0)


# Responses
class CompanyResponse(ORJSONModel):
    image: Union[str, None]
    name: str
    slug: str


class CompanyAnimeResponse(ORJSONModel):
    anime: AnimeResponse
    type: str


class CompaniesSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[CompanyResponse]


class CompanyAnimePaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[CompanyAnimeResponse]
