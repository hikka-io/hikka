from sqlalchemy import select, asc, desc, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from .schemas import AnimeSearchArgsBase
from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from app.utils import new_token
from app import constants
from uuid import UUID

from app.models import (
    EmailMessage,
    AnimeGenre,
    AnimeWatch,
    AuthToken,
    Company,
    Comment,
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


def get_comments_count_subquery(content_id, content_type):
    return (
        select(func.count(Comment.id))
        .filter(
            Comment.content_id == content_id,
            Comment.content_type == content_type,
            Comment.hidden == False,  # noqa: E712
        )
        .scalar_subquery()
    )


def calculate_watch_duration(watch: AnimeWatch) -> int:
    # If anime don't have duration set we just return zero
    if not watch.anime.duration:
        return 0

    # Rewatches duration is calculated from anime episodes_total field
    rewatches_duration = (
        watch.anime.episodes_total * watch.anime.duration * watch.rewatches
        if watch.anime.episodes_total and watch.rewatches
        else 0
    )

    # Current watch duration is just episodes * duration
    episodes_duration = (
        watch.episodes * watch.anime.duration if watch.episodes else 0
    )

    return rewatches_duration + episodes_duration


# Search stuff
def anime_search_filter(
    search: AnimeSearchArgsBase, query: Select, hide_nsfw=True
):
    if search.years[0]:
        query = query.filter(Anime.year >= search.years[0])

    if search.years[1]:
        query = query.filter(Anime.year <= search.years[1])

    if search.score[0] and search.score[0] > 0:
        query = query.filter(Anime.score >= search.score[0])

    if search.score[1]:
        query = query.filter(Anime.score <= search.score[1])

    if len(search.season) > 0:
        query = query.filter(Anime.season.in_(search.season))

    if len(search.rating) > 0:
        query = query.filter(Anime.rating.in_(search.rating))

    # In some cases, like on front page, we would want to hide NSFW content
    if len(search.rating) == 0 and hide_nsfw:
        # No hentai (RX) by default
        query = query.filter(
            Anime.rating.in_(
                [
                    constants.AGE_RATING_R_PLUS,
                    constants.AGE_RATING_PG_13,
                    constants.AGE_RATING_PG,
                    constants.AGE_RATING_G,
                    constants.AGE_RATING_R,
                ]
            )
        )

    if len(search.status) > 0:
        query = query.filter(Anime.status.in_(search.status))

    if len(search.source) > 0:
        query = query.filter(Anime.source.in_(search.source))

    if len(search.media_type) > 0:
        query = query.filter(Anime.media_type.in_(search.media_type))

    if search.only_translated:
        query = query.filter(Anime.translated_ua == True)  # noqa: E712

    if len(search.producers) > 0:
        query = query.join(Anime.producers).filter(
            Company.slug.in_(search.producers)
        )

    if len(search.studios) > 0:
        query = query.join(Anime.studios).filter(
            Company.slug.in_(search.studios)
        )

    # All genres must be present in query result
    if len(search.genres) > 0:
        query = query.filter(
            and_(
                *[
                    Anime.genres.any(AnimeGenre.slug == slug)
                    for slug in search.genres
                ]
            )
        )

    return query
