from pydantic import Field
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    CompanyResponse,
    CompanyTypeEnum,
    AnimeResponse,
    CustomModel,
)


# Enums
class CompanyAnimeTypeEnum(str, Enum):
    producer = constants.COMPANY_ANIME_PRODUCER
    studio = constants.COMPANY_ANIME_STUDIO


# Args
class CompanyAnimeArgs(CustomModel):
    page: int = Field(default=1, gt=0, example=1)
    type: CompanyAnimeTypeEnum | None = None


# Responses
class CompanyAnimeResponse(CustomModel):
    anime: AnimeResponse
    type: CompanyTypeEnum


class CompaniesSearchPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CompanyResponse]


class CompanyAnimePaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[CompanyAnimeResponse]
