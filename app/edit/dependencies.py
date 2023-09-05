from app.dependencies import auth_required, get_anime_by_slug
from app.models import User, Anime, ContentEdit
from sqlalchemy.ext.asyncio import AsyncSession
from app.service import get_anime_by_id
from app.database import get_session
from .service import get_edit_by_id
from app.errors import Abort
from fastapi import Depends
from app import constants

from .schemas import (
    AnimeEditArgs,
)


async def verify_edit_perms(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_CREATE_EDIT])
    ),
) -> User:
    return user


async def verify_review_perms(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            permissions=[
                constants.PERMISSION_ACCEPT_EDIT,
                constants.PERMISSION_REJECT_EDIT,
            ]
        )
    ),
) -> User:
    return user


# ToDo: move this to a model_validator once we migrate to Pydantic 2
async def validate_anime_args(args: AnimeEditArgs) -> AnimeEditArgs:
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


async def verify_anime_edit(
    edit_id: int,
    session: AsyncSession = Depends(get_session),
) -> ContentEdit:
    if not (edit := await get_edit_by_id(session, edit_id)):
        raise Abort("edit", "invalid-id")

    if edit.status != constants.EDIT_PENDING:
        raise Abort("edit", "already-reviewed")

    if edit.content_type != constants.CONTENT_ANIME:
        raise Abort("edit", "wrong-content-type")

    if not (await get_anime_by_id(session, edit.content_id)):
        raise Abort("edit", "invalid-content-id")

    return edit
