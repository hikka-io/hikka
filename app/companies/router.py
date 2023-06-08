from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import QuerySearchArgs
from fastapi import APIRouter, Depends
from .dependencies import get_company
from app.database import get_session
from app.models import Company
from app import meilisearch
from app import constants
from . import service

from .schemas import (
    CompaniesSearchPaginationResponse,
    CompanyAnimePaginationResponse,
    CompanyAnimeArgs,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("", response_model=CompaniesSearchPaginationResponse)
async def search_companies(
    search: QuerySearchArgs,
    session: AsyncSession = Depends(get_session),
):
    if not search.query:
        limit, offset = pagination(search.page)
        total = await service.search_total(session)
        result = await service.companies_search(session, limit, offset)
        return {
            "pagination": pagination_dict(total, search.page, limit),
            "list": [company for company in result],
        }

    return await meilisearch.search(
        constants.SEARCH_INDEX_COMPANIES,
        sort=["favorites:desc"],
        query=search.query,
        page=search.page,
    )


@router.get("/{slug}/anime", response_model=CompanyAnimePaginationResponse)
async def company_anime(
    args: CompanyAnimeArgs = Depends(),
    company: Company = Depends(get_company),
    session: AsyncSession = Depends(get_session),
):
    limit, offset = pagination(args.page)
    total = await service.company_anime_total(session, company, args.type)
    result = await service.company_anime(
        session, company, args.type, limit, offset
    )

    return {
        "pagination": pagination_dict(total, args.page, limit),
        "list": [entry for entry in result],
    }
