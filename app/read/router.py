from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Manga, Novel, Read
from app.dependencies import get_page, get_size
from app.dependencies import auth_required
from app.schemas import SuccessResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from . import service

from app.utils import (
    pagination_dict,
    pagination,
)

from .schemas import (
    UserReadPaginationResponse,
    ReadContentTypeEnum,
    ReadResponse,
    ReadArgs,
)

from .dependencies import (
    verify_read_content,
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
    user: User = Depends(auth_required()),
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
    user: User = Depends(auth_required()),
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
    user: User = Depends(auth_required()),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_manga_read_following_total(
        session, user, content_type, content
    )

    read = await service.get_manga_read_following(
        session, user, content_type, content, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": read.unique().all(),
    }
