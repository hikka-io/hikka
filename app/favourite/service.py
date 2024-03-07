from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from datetime import datetime
from app import constants

from app.service import (
    anime_loadonly,
    create_log,
)

from app.models import (
    AnimeFavourite,
    AnimeWatch,
    Anime,
    User,
)


async def get_favourite(
    session: AsyncSession, anime: AnimeFavourite, user: User
) -> AnimeFavourite | None:
    return await session.scalar(
        select(AnimeFavourite).filter(
            AnimeFavourite.anime == anime,
            AnimeFavourite.user == user,
        )
    )


async def create_favourite(
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

    await create_log(
        session,
        constants.LOG_FAVOURITE_ANIME,
        user,
        anime.id,
    )

    return favourite


async def delete_favourite(session: AsyncSession, favourite: AnimeFavourite):
    await session.delete(favourite)
    await session.commit()

    await create_log(
        session,
        constants.LOG_FAVOURITE_ANIME_REMOVE,
        favourite.user,
        favourite.anime.id,
    )


async def get_user_favourite_list(
    session: AsyncSession,
    user: User,
    request_user: User | None,
    limit: int,
    offset: int,
) -> list[AnimeFavourite]:
    # Load request user watch statuses here
    load_options = [
        anime_loadonly(joinedload(AnimeFavourite.anime)).joinedload(
            Anime.watch
        ),
        with_loader_criteria(
            AnimeWatch,
            AnimeWatch.user_id == request_user.id if request_user else None,
        ),
    ]

    return await session.scalars(
        select(AnimeFavourite)
        .filter(AnimeFavourite.user == user)
        .order_by(desc(AnimeFavourite.created))
        .options(*load_options)
        .limit(limit)
        .offset(offset)
    )


async def get_user_favourite_list_count(
    session: AsyncSession,
    user: User,
) -> int:
    return await session.scalar(
        select(func.count(AnimeFavourite.id)).filter(
            AnimeFavourite.user == user
        )
    )
