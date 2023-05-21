from app.schemas import WatchResponse, SuccessResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Anime, AnimeWatch
from fastapi import APIRouter, Depends
from app.database import get_session
from .schemas import WatchArgs
from typing import Tuple
from . import service

from .dependencies import (
    verify_add_watch,
    verify_watch,
)


router = APIRouter(prefix="/watch", tags=["Watch"])


@router.get("/{slug}", response_model=WatchResponse)
async def watch_get(watch: AnimeWatch = Depends(verify_watch)):
    return watch


@router.put("/{slug}", response_model=WatchResponse)
async def watch_add(
    data: Tuple[Anime, User, WatchArgs] = Depends(verify_add_watch),
    session: AsyncSession = Depends(get_session),
):
    return await service.save_watch(session, *data)


@router.delete("/{slug}", response_model=SuccessResponse)
async def delete_watch(
    watch: AnimeWatch = Depends(verify_watch),
    session: AsyncSession = Depends(get_session),
):
    await service.delete_watch(session, watch)
    return {"success": True}
