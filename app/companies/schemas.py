from pydantic import constr
from pydantic import Field
from app import constants
from typing import Union
from enum import Enum

from app.schemas import (
    PaginationResponse,
    CompanyResponse,
    CompanyTypeEnum,
    AnimeResponse,
    ORJSONModel,
)


# Enums
class CompanyAnimeTypeEnum(str, Enum):
    producer = constants.COMPANY_ANIME_PRODUCER
    studio = constants.COMPANY_ANIME_STUDIO


# Args
class CompanyAnimeArgs(ORJSONModel):
    type: Union[CompanyAnimeTypeEnum, None] = None
    page: int = Field(default=1, gt=0, example=1)


# Responses
class CompanyAnimeResponse(ORJSONModel):
    anime: AnimeResponse
    type: CompanyTypeEnum


class CompaniesSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[CompanyResponse]


class CompanyAnimePaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[CompanyAnimeResponse]
