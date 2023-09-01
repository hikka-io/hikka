from app.dependencies import auth_required, get_anime_by_slug
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import User, Anime
from app.errors import Abort
from fastapi import Depends
from app import constants

from .schemas import (
    EditAnimeArgs,
)


async def verify_edit_perms(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_CREATE_EDIT])
    ),
) -> User:
    return user


# ToDo: move this to a model_validator once we migrate to Pydantic 2
async def validate_anime_args(args: EditAnimeArgs) -> EditAnimeArgs:
    for arg in args:
        if arg[1] is not None:
            return args

    raise Abort("edit", "empty-edit")


async def validate_content_slug(
    slug: str,
    session: AsyncSession = Depends(get_session),
) -> Anime:
    if not (anime := await get_anime_by_slug(session, slug)):
        raise Abort("anime", "not-found")

    return anime
