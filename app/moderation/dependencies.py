from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.errors import Abort
from fastapi import Depends

from .schemas import ModerationSearchArgs

from app.service import (
    get_user_by_username,
)


async def validate_moderation_search_args(
    args: ModerationSearchArgs,
    session: AsyncSession = Depends(get_session),
):
    if args.author:
        if not await get_user_by_username(session, args.author):
            raise Abort("edit", "author-not-found")

    return args
