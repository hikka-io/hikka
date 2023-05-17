from tortoise.fields.relational import ManyToManyRelation
from app.service import get_user_by_username
from app.dependencies import auth_required
from app.errors import Abort
from app.models import User
from fastapi import Depends
from typing import Tuple
from . import service

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session


async def validate_username(
    username: str, session: AsyncSession = Depends(get_session)
) -> User:
    if not (user := await get_user_by_username(session, username)):
        raise Abort("user", "not-found")

    return user


async def validate_self(
    follow_user: User = Depends(validate_username),
    user: User = Depends(auth_required),
) -> Tuple[User, User]:
    if follow_user == user:
        raise Abort("follow", "self")

    return follow_user, user


async def validate_follow(
    users: Tuple[User, User] = Depends(validate_self),
    session: AsyncSession = Depends(get_session),
) -> Tuple[User, User]:
    if await service.is_following(session, *users):
        raise Abort("follow", "already-following")

    return users


async def validate_unfollow(
    users: Tuple[User, User] = Depends(validate_self),
    session: AsyncSession = Depends(get_session),
) -> Tuple[User, User]:
    if not await service.is_following(session, *users):
        raise Abort("follow", "not-following")

    return users


async def validate_action(action: str) -> str:
    if action not in ["following", "followers"]:
        raise Abort("follow", "invalid-action")

    return action
