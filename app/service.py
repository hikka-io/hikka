from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, AuthToken, Anime
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import Union


async def get_user_by_username(
    session: AsyncSession, username: str
) -> Union[User, None]:
    return await session.scalar(select(User).filter_by(username=username))


async def get_anime_by_slug(
    session: AsyncSession, slug: str
) -> Union[Anime, None]:
    return await session.scalar(select(Anime).filter_by(slug=slug))


async def get_anime_by_id(session: AsyncSession, id: str) -> Union[Anime, None]:
    return await session.scalar(select(Anime).filter_by(id=id))


async def get_auth_token(
    session: AsyncSession, secret: str
) -> Union[AuthToken, None]:
    return await session.scalar(
        select(AuthToken)
        .filter_by(secret=secret)
        .options(selectinload(AuthToken.user))
    )


def anime_loadonly(statement):
    return statement.load_only(
        Anime.episodes_released,
        Anime.episodes_total,
        Anime.content_id,
        Anime.media_type,
        Anime.scored_by,
        Anime.title_ja,
        Anime.title_en,
        Anime.title_ua,
        Anime.status,
        Anime.score,
        Anime.slug,
    )
