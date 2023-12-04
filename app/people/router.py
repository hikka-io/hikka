from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_page, get_size
from fastapi import APIRouter, Depends
from app.database import get_session
from .dependencies import get_person
from app.models import Person
from app import meilisearch
from app import constants
from . import service

from app.schemas import (
    QuerySearchArgs,
    PersonResponse,
)

from .schemas import (
    PersonSearchPaginationResponse,
    PersonAnimePaginationResponse,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/people", tags=["People"])


@router.get("/{slug}", response_model=PersonResponse)
async def person_info(person: Person = Depends(get_person)):
    return person


@router.post("", response_model=PersonSearchPaginationResponse)
async def search_people(
    search: QuerySearchArgs,
    session: AsyncSession = Depends(get_session),
):
    if not search.query:
        limit, offset = pagination(search.page)
        total = await service.search_total(session)
        people = await service.people_search(session, limit, offset)
        return {
            "pagination": pagination_dict(total, search.page, limit),
            "list": people.all(),
        }

    return await meilisearch.search(
        constants.SEARCH_INDEX_PEOPLE,
        sort=["favorites:desc"],
        query=search.query,
        page=search.page,
    )


@router.get("/{slug}/anime", response_model=PersonAnimePaginationResponse)
async def character_anime(
    session: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.person_anime_total(session, person)
    anime = await service.person_anime(session, person, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": anime.all(),
    }
