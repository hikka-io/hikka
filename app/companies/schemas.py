from app.schemas import ORJSONModel, PaginationResponse
from pydantic import constr
from pydantic import Field
from typing import Union


# Args
class CompaniesSearchArgs(ORJSONModel):
    query: Union[constr(min_length=3, max_length=255), None] = None
    page: int = Field(default=1, gt=0)


# Responses
class CompanyResponse(ORJSONModel):
    image: Union[str, None]
    name: str
    slug: str


class CompaniesSearchPaginationResponse(ORJSONModel):
    pagination: PaginationResponse
    list: list[CompanyResponse]
