from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import QuerySearchArgs
from fastapi import APIRouter, Depends
from app.dependencies import get_page
from app.database import get_session
from .dependencies import get_person
from app.models import Person
from app import meilisearch
from app import constants
from . import service

from .schemas import (
    PersonSearchPaginationResponse,
    PersonAnimePaginationResponse,
)

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
    if not search.query:
        total = await service.search_total(session)
        limit, offset = pagination(search.page, constants.SEARCH_RESULT_LIMIT)
        result = await service.people_search(session, limit, offset)
        return {
            "pagination": pagination_dict(total, search.page, limit),
            "list": [character for character in result],
        }

    return await meilisearch.search(
        constants.SEARCH_INDEX_PEOPLE,
        sort=["favorites:desc"],
        query=search.query,
        page=search.page,
    )


@router.get("/{slug}/anime", response_model=PersonAnimePaginationResponse)
async def character_anime(
    page: int = Depends(get_page),
    person: Person = Depends(get_person),
    session: AsyncSession = Depends(get_session),
):
    total = await service.person_anime_total(session, person)
    limit, offset = pagination(page, constants.SEARCH_RESULT_LIMIT)
    result = await service.person_anime(session, person, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": [entry for entry in result],
    }
