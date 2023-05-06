from app.models import User, Anime, AnimeWatch
from fastapi import APIRouter, Depends
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
    return display.watch(watch)


@router.put("/{slug}", response_model=WatchResponse)
async def watch_add(
    data: Tuple[Anime, User, WatchArgs] = Depends(verify_add_watch)
):
    watch = await service.save_watch(*data)
    return display.watch(watch)


@router.delete("/{slug}", response_model=WatchDeleteResponse)
async def delete_watch(watch: AnimeWatch = Depends(verify_watch)):
    await service.delete_watch(watch)
    return {"success": True}
