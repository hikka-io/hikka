from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from app.utils import new_token
from uuid import UUID

from app.models import (
    EmailMessage,
    AnimeWatch,
    AuthToken,
    Anime,
    User,
    Log,
)


async def get_anime_watch(session: AsyncSession, anime: Anime, user: User):
    return await session.scalar(
        select(AnimeWatch).filter(
            AnimeWatch.anime == anime,
            AnimeWatch.user == user,
        )
    )


async def get_user_by_username(
    session: AsyncSession, username: str
) -> User | None:
    return await session.scalar(
        select(User).filter(func.lower(User.username) == username.lower())
    )


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    return await session.scalar(
        select(User).filter(func.lower(User.email) == email.lower())
    )


async def get_anime_by_slug(session: AsyncSession, slug: str) -> Anime | None:
    return await session.scalar(
        select(Anime).filter(func.lower(Anime.slug) == slug.lower())
    )


async def get_anime_by_id(session: AsyncSession, id: str) -> Anime | None:
    return await session.scalar(select(Anime).filter(Anime.id == id))


async def get_auth_token(
    session: AsyncSession, secret: str
) -> AuthToken | None:
    return await session.scalar(
        select(AuthToken)
        .filter(AuthToken.secret == secret)
        .options(selectinload(AuthToken.user))
    )


async def create_activation_token(session: AsyncSession, user: User) -> User:
    # Generate new token
    user.activation_expire = datetime.utcnow() + timedelta(hours=3)
    user.activation_token = new_token()

    session.add(user)
    await session.commit()

    return user


async def create_email(
    session: AsyncSession, email_type: str, content: str, user: User
) -> EmailMessage:
    message = EmailMessage(
        **{
            "created": datetime.utcnow(),
            "content": content,
            "type": email_type,
            "user": user,
        }
    )

    session.add(message)
    await session.commit()

    return message


def anime_loadonly(statement):
    return statement.load_only(
        Anime.episodes_released,
        Anime.episodes_total,
        Anime.translated_ua,
        Anime.content_id,
        Anime.media_type,
        Anime.scored_by,
        Anime.title_ja,
        Anime.title_en,
        Anime.title_ua,
        Anime.season,
        Anime.source,
        Anime.status,
        Anime.rating,
        Anime.score,
        Anime.slug,
        Anime.year,
    )


async def create_log(
    session: AsyncSession,
    log_type: str,
    user: User,
    target_id: UUID | None = None,
    data: dict = {},
):
    now = datetime.utcnow()

    log = Log(
        **{
            "created": now,
            "target_id": target_id,
            "log_type": log_type,
            "user": user,
            "data": data,
        }
    )

    session.add(log)
    await session.commit()

    return log
