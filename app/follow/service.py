from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, case
from sqlalchemy.orm import with_expression
from app.models import User, Follow
from app.utils import utcnow
from app import constants

from app.service import (
    get_followed_user_ids,
    create_log,
)


async def count_followers(session: AsyncSession, user: User):
    return await session.scalar(
        select(func.count(Follow.id)).filter(Follow.followed_user == user)
    )


async def count_following(session: AsyncSession, user: User):
    return await session.scalar(
        select(func.count(Follow.id)).filter(Follow.user == user)
    )


async def get_follow(session: AsyncSession, followed_user: User, user: User):
    return await session.scalar(
        select(Follow).filter(
            Follow.followed_user == followed_user,
            Follow.user == user,
        )
    )


async def is_following(session: AsyncSession, followed_user: User, user: User):
    return await get_follow(session, followed_user, user) is not None


async def follow(session: AsyncSession, followed_user: User, user: User):
    follow = Follow(
        **{
            "followed_user": followed_user,
            "created": utcnow(),
            "user": user,
        }
    )

    session.add(follow)
    await session.commit()

    await create_log(
        session,
        constants.LOG_FOLLOW,
        user,
        followed_user.id,
    )

    return True


async def unfollow(session: AsyncSession, followed_user: User, user: User):
    follow = await get_follow(session, followed_user, user)

    await session.delete(follow)
    await session.commit()

    await create_log(
        session,
        constants.LOG_UNFOLLOW,
        user,
        followed_user.id,
    )

    return False


async def list_following(
    session: AsyncSession,
    request_user: User | None,
    user: User,
    limit: int,
    offset: int,
):
    followed_user_ids = await get_followed_user_ids(session, request_user)

    return await session.scalars(
        select(User)
        .join(Follow, Follow.followed_user_id == User.id)
        .filter(Follow.user_id == user.id)
        .order_by(desc(Follow.created))
        .options(
            with_expression(
                User.is_followed,
                case((User.id.in_(followed_user_ids), True), else_=False),
            )
        )
        .limit(limit)
        .offset(offset)
    )


async def list_followers(
    session: AsyncSession,
    request_user: User | None,
    user: User,
    limit: int,
    offset: int,
):
    followed_user_ids = await get_followed_user_ids(session, request_user)

    return await session.scalars(
        select(User)
        .join(Follow, Follow.user_id == User.id)
        .filter(Follow.followed_user_id == user.id)
        .order_by(desc(Follow.created))
        .options(
            with_expression(
                User.is_followed,
                case((User.id.in_(followed_user_ids), True), else_=False),
            )
        )
        .limit(limit)
        .offset(offset)
    )
