from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from typing import Tuple
from . import service

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/characters", tags=["Characters"])


@router.post("")
async def search_characters(
    # search: CompaniesSearchArgs,
    session: AsyncSession = Depends(get_session),
):
    page = 1
    # if not search.query:
    total = await service.search_total(session)

    limit, offset = pagination(
        page,
        limit=constants.SEARCH_RESULT_LIMIT,
    )

    result = await service.characters_search(session, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": [character for character in result],
    }

    # return await meilisearch.companies_search(search)
