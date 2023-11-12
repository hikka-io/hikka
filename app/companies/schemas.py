from pydantic import Field
from app import constants
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
    page: int = Field(default=1, gt=0, example=1)
    type: CompanyAnimeTypeEnum | None = None


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
