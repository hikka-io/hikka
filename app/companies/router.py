from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from . import meilisearch
from . import service

from .schemas import (
    CompaniesSearchPaginationResponse,
    CompaniesSearchArgs,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("", response_model=CompaniesSearchPaginationResponse)
async def search_companies(
    search: CompaniesSearchArgs,
    session: AsyncSession = Depends(get_session),
):
    if not search.query:
        total = await service.search_total(session)

        limit, offset = pagination(
            search.page,
            limit=constants.SEARCH_RESULT_LIMIT,
        )

        result = await service.companies_search(session, limit, offset)

        return {
            "pagination": pagination_dict(total, search.page, limit),
            "list": [company for company in result],
        }

    return await meilisearch.companies_search(search)
