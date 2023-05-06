from .schemas import FavouriteResponse, DeleteResponse
from app.models import User, Anime, AnimeFavourite
from fastapi import APIRouter, Depends
from typing import Tuple
from . import service

from .dependencies import (
    get_anime_favourite,
    add_anime_favourite,
)


# ToDo: Better responses
router = APIRouter(prefix="/favourite")


@router.get("/anime/{slug}", response_model=FavouriteResponse)
async def anime_favourite(
    favourite: AnimeFavourite = Depends(get_anime_favourite),
):
    return {"created": favourite.created}


@router.put("/anime/{slug}", response_model=FavouriteResponse)
async def anime_favourite_add(
    data: Tuple[Anime, User] = Depends(add_anime_favourite)
):
    favourite = await service.create_anime_favourite(*data)
    return {"created": favourite.created}


@router.delete("/anime/{slug}", response_model=DeleteResponse)
async def anime_favourite_delete(
    favourite: AnimeFavourite = Depends(get_anime_favourite),
):
    await service.delete_anime_favourite(favourite)
    return {"success": True}
