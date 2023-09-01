from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User, Anime
from . import service

from .dependencies import (
    validate_content_slug,
    validate_anime_args,
    verify_edit_perms,
)

from .schemas import (
    EditAnimeArgs,
)


router = APIRouter(prefix="/edit", tags=["Edit"])


@router.post(
    "/anime/{slug}",
    response_model=None,
)
async def edit_content(
    args: EditAnimeArgs = Depends(validate_anime_args),
    user: User = Depends(verify_edit_perms),
    anime: Anime = Depends(validate_content_slug),
    session: AsyncSession = Depends(get_session),
):
    return await service.create_anime_edit_request(args, user, anime, session)
