from .schemas import AnimeFavouritePaginationResponse
from app.models import User, Anime, AnimeFavourite
from app.utils import pagination, pagination_dict
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from typing import Tuple
from . import service

from app.dependencies import (
    get_user,
    get_page,
    get_size,
)

from app.schemas import (
    AnimeFavouriteResponse,
    SuccessResponse,
)

from .dependencies import (
    get_anime_favourite,
    add_anime_favourite,
)


router = APIRouter(prefix="/favourite", tags=["Favourite"])


@router.get("/anime/{slug}", response_model=AnimeFavouriteResponse)
async def anime_favourite(
    favourite: AnimeFavourite = Depends(get_anime_favourite),
):
    return favourite


@router.put("/anime/{slug}", response_model=AnimeFavouriteResponse)
async def anime_favourite_add(
    data: Tuple[Anime, User] = Depends(add_anime_favourite),
    session: AsyncSession = Depends(get_session),
):
    return await service.create_anime_favourite(session, *data)


@router.delete("/anime/{slug}", response_model=SuccessResponse)
async def anime_favourite_delete(
    favourite: AnimeFavourite = Depends(get_anime_favourite),
    session: AsyncSession = Depends(get_session),
):
    await service.delete_anime_favourite(session, favourite)
    return {"success": True}


@router.get(
    "/anime/{username}/list",
    response_model=AnimeFavouritePaginationResponse,
)
async def anime_favourite_list(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_user_anime_favourite_list_count(session, user)
    anime = await service.get_user_anime_favourite_list(
        session, user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": anime.all(),
    }
