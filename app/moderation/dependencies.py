from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.dependencies import auth_required
from app.models.user.user import User
from app.database import get_session
from app.errors import Abort
from app import constants
from app.service import (
    get_user_by_username,
)

from .schemas import ModerationSearchArgs


async def validate_moderation_search_args(
    args: ModerationSearchArgs,
    session: AsyncSession = Depends(get_session),
):
    if args.author:
        if not await get_user_by_username(session, args.author):
            raise Abort("edit", "author-not-found")

    return args


async def validate_moderation_role(
    author: User = Depends(
        auth_required(
            optional=False,
            scope=[constants.ROLE_MODERATOR, constants.ROLE_ADMIN],
        )
    ),
):
    return author
