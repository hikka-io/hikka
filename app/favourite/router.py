from .schemas import AnimeFavouritePaginationResponse
from app.models import User, Anime, AnimeFavourite
from app.utils import pagination, pagination_dict
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from . import service

from app.dependencies import (
    auth_required,
    get_user,
    get_page,
    get_size,
)

from app.schemas import (
    AnimeFavouriteResponse,
    SuccessResponse,
)

from .dependencies import (
    validate_get_favourite,
    validate_add_favourite,
)


router = APIRouter(prefix="/favourite", tags=["Favourite"])


@router.get("/{content_type}/{slug}", response_model=AnimeFavouriteResponse)
async def get_favourite(
    favourite: AnimeFavourite = Depends(validate_get_favourite),
):
    return favourite


@router.put("/{content_type}/{slug}", response_model=AnimeFavouriteResponse)
async def anime_favourite_add(
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(validate_add_favourite),
    user: User = Depends(auth_required()),
):
    return await service.create_favourite(session, anime, user)


@router.delete("/{content_type}/{slug}", response_model=SuccessResponse)
async def anime_favourite_delete(
    session: AsyncSession = Depends(get_session),
    favourite: AnimeFavourite = Depends(validate_get_favourite),
):
    await service.delete_favourite(session, favourite)
    return {"success": True}


@router.get(
    "/{content_type}/{username}/list",
    response_model=AnimeFavouritePaginationResponse,
)
async def anime_favourite_list(
    content_type: str,
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(auth_required(optional=True)),
    user: User = Depends(get_user),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_user_favourite_list_count(session, user)
    anime = await service.get_user_favourite_list(
        session, user, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": anime.unique().all(),
    }
