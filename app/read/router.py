from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Manga, Novel, Read
from app.dependencies import auth_required
from app.schemas import SuccessResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from . import service

from .schemas import (
    ReadContentTypeEnum,
    ReadResponse,
    ReadArgs,
)

from .dependencies import (
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
