from app.models import AnimeFavourite, Anime, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from app.service import anime_loadonly
from datetime import datetime


async def get_anime_favourite(
    session: AsyncSession, anime: AnimeFavourite, user: User
) -> AnimeFavourite | None:
    return await session.scalar(
        select(AnimeFavourite).filter(
            AnimeFavourite.anime == anime,
            AnimeFavourite.user == user,
        )
    )


async def create_anime_favourite(
    session: AsyncSession, anime: Anime, user: User
) -> AnimeFavourite:
    favourite = AnimeFavourite(
        **{
            "created": datetime.utcnow(),
            "anime": anime,
            "user": user,
        }
    )

    session.add(favourite)
    await session.commit()

    return favourite


async def delete_anime_favourite(
    session: AsyncSession, favourite: AnimeFavourite
):
    await session.delete(favourite)
    await session.commit()


async def get_user_anime_favourite_list(
    session: AsyncSession,
    user: User,
    limit: int,
    offset: int,
) -> list[AnimeFavourite]:
    return await session.scalars(
        select(AnimeFavourite)
        .filter(AnimeFavourite.user == user)
        .order_by(desc(AnimeFavourite.created))
        .options(anime_loadonly(selectinload(AnimeFavourite.anime)))
        .limit(limit)
        .offset(offset)
    )


async def get_user_anime_favourite_list_count(
    session: AsyncSession,
    user: User,
) -> int:
    return await session.scalar(
        select(func.count(AnimeFavourite.id)).filter(
            AnimeFavourite.user == user
        )
    )
