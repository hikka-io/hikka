from app.schemas import MangaResponse, NovelResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Manga, Novel, Read
from app.schemas import SuccessResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from . import service

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
    get_user,
)

from app.utils import (
    pagination_dict,
    pagination,
)

from .schemas import (
    UserReadPaginationResponse,
    ReadPaginationResponse,
    ReadContentTypeEnum,
    ReadStatsResponse,
    ReadStatusEnum,
    ReadSearchArgs,
    ReadResponse,
    ReadArgs,
)

from .dependencies import (
    verify_read_content,
    verify_user_random,
    verify_add_read,
    verify_read,
)


router = APIRouter(prefix="/read", tags=["Read"])


@router.get("/{content_type}/{slug}", response_model=ReadResponse)
async def read_get(read: Read = Depends(verify_read)):
    return read


@router.put("/{content_type}/{slug}", response_model=ReadResponse)
async def read_add(
    args: ReadArgs,
    content_type: ReadContentTypeEnum,
    session: AsyncSession = Depends(get_session),
    content: Manga | Novel = Depends(verify_add_read),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_UPDATE_READLIST])
    ),
):
    return await service.save_read(
        session,
        content_type,
        content,
        user,
        args,
    )


@router.delete("/{content_type}/{slug}", response_model=SuccessResponse)
async def delete_read(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_UPDATE_READLIST])
    ),
    read: Read = Depends(verify_read),
):
    await service.delete_read(session, read, user)
    return {"success": True}


@router.get(
    "/{content_type}/{slug}/following",
    response_model=UserReadPaginationResponse,
)
async def get_read_following(
    content_type: ReadContentTypeEnum,
    session: AsyncSession = Depends(get_session),
    content: Manga | Novel = Depends(verify_read_content),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_READ_USER_DETAILS])
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_read_following_total(
        session, user, content_type, content
    )

    read = await service.get_read_following(
        session, user, content_type, content, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": read.unique().all(),
    }


@router.get(
    "/{content_type}/{username}/stats",
    summary="Get user read list stats",
    response_model=ReadStatsResponse,
)
async def user_read_stats(
    content_type: ReadContentTypeEnum,
    user: User = Depends(get_user),
):
    if content_type == constants.CONTENT_MANGA:
        return user.manga_stats

    if content_type == constants.CONTENT_NOVEL:
        return user.novel_stats


@router.get(
    "/{content_type}/random/{username}/{status}",
    response_model=MangaResponse | NovelResponse,
)
async def random_read_novel(
    status: ReadStatusEnum,
    content_type: ReadContentTypeEnum,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(verify_user_random),
):
    return await service.random_read(
        session,
        user,
        content_type,
        status,
    )


@router.post(
    "/{content_type}/{username}/list",
    response_model=ReadPaginationResponse,
)
async def user_read_list(
    search: ReadSearchArgs,
    content_type: ReadContentTypeEnum,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)

    total = await service.get_user_read_list_count(
        session, search, content_type, user
    )

    read = await service.get_user_read_list(
        session, search, content_type, user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": read.all(),
    }
