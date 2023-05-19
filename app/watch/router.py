from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Anime, AnimeWatch
from fastapi import APIRouter, Depends
from app.database import get_session
from typing import Tuple
from app import display
from . import service

from .dependencies import (
    verify_add_watch,
    verify_watch,
)

from .schemas import (
    WatchDeleteResponse,
    WatchResponse,
    WatchArgs,
)


router = APIRouter(prefix="/watch")


@router.get("/{slug}", response_model=WatchResponse)
async def watch_get(watch: AnimeWatch = Depends(verify_watch)):
    return watch


@router.put("/{slug}", response_model=WatchResponse)
async def watch_add(
    data: Tuple[Anime, User, WatchArgs] = Depends(verify_add_watch),
    session: AsyncSession = Depends(get_session),
):
    watch = await service.save_watch(session, *data)
    return watch


@router.delete("/{slug}", response_model=WatchDeleteResponse)
async def delete_watch(
    watch: AnimeWatch = Depends(verify_watch),
    session: AsyncSession = Depends(get_session),
):
    await service.delete_watch(session, watch)
    return {"success": True}
