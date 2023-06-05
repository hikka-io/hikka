from .schemas import PersonSearchPaginationResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import QuerySearchArgs
from fastapi import APIRouter, Depends
from app.dependencies import get_page
from app.database import get_session
from app.models import Person
from app import constants
from . import service

from app.utils import (
    pagination_dict,
    pagination,
)

router = APIRouter(prefix="/people", tags=["People"])


@router.post("", response_model=PersonSearchPaginationResponse)
async def search_people(
    search: QuerySearchArgs,
    session: AsyncSession = Depends(get_session),
):
    # if not search.query:
    total = await service.search_total(session)

    limit, offset = pagination(
        search.page,
        limit=constants.SEARCH_RESULT_LIMIT,
    )

    result = await service.people_search(session, limit, offset)

    return {
        "pagination": pagination_dict(total, search.page, limit),
        "list": [character for character in result],
    }

    # return await meilisearch.characters_search(search)
