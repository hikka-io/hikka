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
    paginated_response,
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
    if search.query:
        return await meilisearch.search(
            constants.SEARCH_INDEX_PEOPLE,
            sort=["favorites:desc"],
            query=search.query,
            page=page,
            size=size,
        )

    limit, offset = pagination(page, size)
    total = await service.search_total(session)
    people = await service.people_search(session, limit, offset)

    return paginated_response(people.all(), total, page, limit)


@router.get("/{slug}/anime", response_model=PersonAnimePaginationResponse)
async def person_anime(
    session: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person),
    request_user: User | None = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_WATCHLIST])
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = person.anime_count
    anime = await service.person_anime(
        session, person, request_user, limit, offset
    )

    return paginated_response(anime.unique().all(), total, page, limit)


@router.get("/{slug}/manga", response_model=PersonMangaPaginationResponse)
async def person_manga(
    session: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person),
    request_user: User | None = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_READLIST])
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = person.manga_count
    manga = await service.person_manga(
        session, person, request_user, limit, offset
    )

    return paginated_response(manga.unique().all(), total, page, limit)


@router.get("/{slug}/novel", response_model=PersonNovelPaginationResponse)
async def person_novel(
    session: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person),
    request_user: User | None = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_READLIST])
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = person.novel_count
    novel = await service.person_novel(
        session, person, request_user, limit, offset
    )

    return paginated_response(novel.unique().all(), total, page, limit)


@router.get(
    "/{slug}/characters", response_model=PersonCharactersPaginationResponse
)
async def person_voices(
    session: AsyncSession = Depends(get_session),
    person: Person = Depends(get_person),
    request_user: User | None = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_WATCHLIST])
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = person.characters_count
    voices = await service.person_voices(
        session, person, request_user, limit, offset
    )

    return paginated_response(voices.unique().all(), total, page, limit)
