from app.models import AnimeFavourite, Anime, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Union


async def get_anime_favourite(
    session: AsyncSession, anime: AnimeFavourite, user: User
) -> Union[AnimeFavourite, None]:
    return await session.scalar(
        select(AnimeFavourite).filter_by(anime=anime, user=user)
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
