from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Anime, ContentEdit
from fastapi import APIRouter, Depends
from app.database import get_session
from . import service

from .dependencies import (
    validate_content_slug,
    validate_anime_args,
    verify_review_perms,
    verify_edit_perms,
    verify_anime_edit,
)

from .schemas import (
    AnimeEditResponse,
    AnimeEditArgs,
)


router = APIRouter(prefix="/edit", tags=["Edit"])


@router.post(
    "/anime/{slug}",
    response_model=AnimeEditResponse,
)
async def edit_anime(
    args: AnimeEditArgs = Depends(validate_anime_args),
    user: User = Depends(verify_edit_perms),
    anime: Anime = Depends(validate_content_slug),
    session: AsyncSession = Depends(get_session),
):
    return await service.create_anime_edit_request(args, user, anime, session)


@router.post(
    "/anime/{edit_id}/approve",
    response_model=AnimeEditResponse,
)
async def approve_anime_edit(
    user: User = Depends(verify_review_perms),
    edit: ContentEdit = Depends(verify_anime_edit),
    session: AsyncSession = Depends(get_session),
):
    return await service.approve_anime_edit_request(user, edit, session)


@router.post(
    "/anime/{edit_id}/deny",
    response_model=AnimeEditResponse,
)
async def deny_anime_edit(
    user: User = Depends(verify_review_perms),
    edit: ContentEdit = Depends(verify_anime_edit),
    session: AsyncSession = Depends(get_session),
):
    return await service.deny_anime_edit_request(user, edit, session)
