from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import QuerySearchArgs
from fastapi import APIRouter, Depends
from app.database import get_session
from .dependencies import get_person
from app.models import Person, User
from app import meilisearch
from app import constants
from . import service

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)

from .schemas import (
    PersonCharactersPaginationResponse,
    PersonSearchPaginationResponse,
    PersonAnimePaginationResponse,
    PersonMangaPaginationResponse,
    PersonNovelPaginationResponse,
    PersonCountResponse,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/people", tags=["People"])


@router.get("/{slug}", response_model=PersonCountResponse)
async def person_info(person: Person = Depends(get_person)):
    return person


@router.post("", response_model=PersonSearchPaginationResponse)
async def search_people(
    search: QuerySearchArgs,
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    if not search.query:
        limit, offset = pagination(page, size)
        total = await service.search_total(session)
        people = await service.people_search(session, limit, offset)
        return {
            "pagination": pagination_dict(total, page, limit),
            "list": people.all(),
        }

    return await meilisearch.search(
        constants.SEARCH_INDEX_PEOPLE,
        sort=["favorites:desc"],
        query=search.query,
        page=page,
        size=size,
    )


@router.get("/{slug}/anime", response_model=PersonAnimePaginationResponse)
async def person_anime(
    session: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person),
    request_user: User | None = Depends(auth_required(optional=True)),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.person_anime_total(session, person)
    anime = await service.person_anime(
        session, person, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": anime.unique().all(),
    }


@router.get("/{slug}/manga", response_model=PersonMangaPaginationResponse)
async def person_manga(
    session: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person),
    request_user: User | None = Depends(auth_required(optional=True)),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.person_manga_total(session, person)
    manga = await service.person_manga(
        session, person, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": manga.unique().all(),
    }


@router.get("/{slug}/novel", response_model=PersonNovelPaginationResponse)
async def person_novel(
    session: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person),
    request_user: User | None = Depends(auth_required(optional=True)),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.person_novel_total(session, person)
    novel = await service.person_novel(
        session, person, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": novel.unique().all(),
    }


@router.get(
    "/{slug}/characters", response_model=PersonCharactersPaginationResponse
)
async def person_voices(
    session: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person),
    request_user: User | None = Depends(auth_required(optional=True)),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.person_voices_total(session, person)
    voices = await service.person_voices(
        session, person, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": voices.unique().all(),
    }
