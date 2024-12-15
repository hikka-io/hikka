from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User, Novel
from app import constants
from . import service

from .dependencies import (
    validate_search_novel,
    valdidate_novel_info,
    validate_novel,
)

from .schemas import (
    NovelPaginationResponse,
    NovelInfoResponse,
)

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)

from app.schemas import (
    ContentCharacterPaginationResponse,
    NovelSearchArgs,
)

from app.utils import (
    paginated_response,
    pagination,
)


router = APIRouter(prefix="/novel", tags=["Novel"])


@router.post(
    "",
    response_model=NovelPaginationResponse,
    summary="Novel catalog",
)
async def search_novel(
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_READLIST])
    ),
    search: NovelSearchArgs = Depends(validate_search_novel),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    if search.query:
        return await service.novel_search_query(
            session,
            search,
            request_user,
            page,
            size,
        )

    limit, offset = pagination(page, size)
    total = await service.novel_search_total(session, search)
    novel = await service.novel_search(
        session, search, request_user, limit, offset
    )

    return paginated_response(novel.unique().all(), total, page, limit)


@router.get(
    "/{slug}",
    response_model=NovelInfoResponse,
    summary="Novel info",
)
async def novel_info(novel: Novel = Depends(valdidate_novel_info)):
    return novel


@router.get(
    "/{slug}/characters",
    response_model=ContentCharacterPaginationResponse,
    summary="Novel characters",
)
async def novel_characters(
    session: AsyncSession = Depends(get_session),
    novel: Novel = Depends(validate_novel),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.novel_characters_count(session, novel)
    characters = await service.novel_characters(session, novel, limit, offset)

    return paginated_response(characters.all(), total, page, limit)
