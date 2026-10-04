from app.common.schemas.company import CompanyResponse, CompanyTypeEnum
from app.common.schemas.anime import AnimeResponse
from app import constants
from enum import Enum

from app.schemas import (
    PaginationResponse,
    QuerySearchArgs,
    CustomModel,
)


# Enums
class CompanyAnimeTypeEnum(str, Enum):
    producer = constants.COMPANY_ANIME_PRODUCER
    studio = constants.COMPANY_ANIME_STUDIO


# Args
class CompanyAnimeArgs(CustomModel):
    type: CompanyAnimeTypeEnum | None = None


class CompaniesListArgs(CompanyAnimeArgs, QuerySearchArgs):
    pass


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
