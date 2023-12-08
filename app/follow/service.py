from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_expression
from sqlalchemy import select, desc, func
from app.models import User, Follow
from datetime import datetime
from sqlalchemy import case


async def count_followers(session: AsyncSession, user: User):
    return await session.scalar(
        select(func.count(Follow.id)).where(Follow.followed_user == user)
    )


async def count_following(session: AsyncSession, user: User):
    return await session.scalar(
        select(func.count(Follow.id)).where(Follow.user == user)
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
            "created": datetime.utcnow(),
            "user": user,
        }
    )

    session.add(follow)
    await session.commit()

    return True


async def unfollow(session: AsyncSession, followed_user: User, user: User):
    follow = await get_follow(session, followed_user, user)

    await session.delete(follow)
    await session.commit()

    return False


async def list_following(
    session: AsyncSession,
    request_user: User | None,
    user: User,
    limit: int,
    offset: int,
):
    followed_user_ids = []

    if request_user:
        followed_user_ids = await session.scalars(
            select(Follow.followed_user_id).filter(
                Follow.user_id == request_user.id
            )
        )

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
    followed_user_ids = []

    if request_user:
        followed_user_ids = await session.scalars(
            select(Follow.followed_user_id).filter(
                Follow.user_id == request_user.id
            )
        )

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
