from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.models import User, Follow
from datetime import datetime


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
        select(Follow).filter_by(
            followed_user=followed_user,
            user=user,
        )
    )


async def is_following(session: AsyncSession, followed_user: User, user: User):
    return await get_follow(session, followed_user, user) != None


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

    print(follow.id)

    await session.delete(follow)
    await session.commit()

    return False


async def list_following(
    session: AsyncSession, user: User, limit: int, offset: int
):
    return await session.scalars(
        select(User)
        .select_from(Follow)
        .filter(Follow.user_id == user.id)
        .join(User, Follow.followed_user_id == User.id)
        .order_by(desc(Follow.created))
        .limit(limit)
        .offset(offset)
    )


async def list_followers(
    session: AsyncSession, user: User, limit: int, offset: int
):
    return await session.scalars(
        select(User)
        .select_from(Follow)
        .filter(Follow.followed_user_id == user.id)
        .join(User, Follow.user_id == User.id)
        .order_by(desc(Follow.created))
        .limit(limit)
        .offset(offset)
    )
