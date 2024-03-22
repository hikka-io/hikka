from sqlalchemy import select, asc, desc, and_, func
from app.utils import new_token, is_int, is_uuid
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import with_expression
from .schemas import AnimeSearchArgsBase
from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import joinedload
from app import constants
from uuid import UUID

from app.models import (
    AnimeCollectionContent,
    CollectionContent,
    EmailMessage,
    AnimeGenre,
    Collection,
    AnimeWatch,
    AuthToken,
    Character,
    Company,
    Comment,
    Person,
    Anime,
    Edit,
    User,
    Vote,
    Log,
)


content_type_to_content_class = {
    constants.CONTENT_COLLECTION: Collection,
    constants.CONTENT_CHARACTER: Character,
    constants.CONTENT_SYSTEM_EDIT: Edit,
    constants.CONTENT_COMMENT: Comment,
    constants.CONTENT_PERSON: Person,
    constants.CONTENT_ANIME: Anime,
}


# We use this code mainly with system based on polymorphic identity
async def get_content_by_slug(
    session: AsyncSession, content_type: str, slug: str
):
    """Return content by content_type and slug"""

    content_model = content_type_to_content_class[content_type]
    query = select(content_model)

    # Special case for edit
    if content_type == constants.CONTENT_SYSTEM_EDIT:
        if not is_int(slug):
            return None

        query = query.filter(content_model.edit_id == int(slug))

    # Special case for collection
    # Since collections don't have slugs we use their id instead
    elif content_type == constants.CONTENT_COLLECTION:
        if not is_uuid(slug):
            return None

        query = query.filter(content_model.id == UUID(slug))

    # Special case for comment
    # Since collections don't have slugs we use their id instead
    elif content_type == constants.CONTENT_COMMENT:
        if not is_uuid(slug):
            return None

        query = query.filter(content_model.id == UUID(slug))
        query = query.filter(content_model.hidden == False)  # noqa: E712

    # Everything else is handled here
    else:
        query = query.filter(content_model.slug == slug)

    return await session.scalar(query)


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


def build_order_by(sort: list[str]):
    order_mapping = {
        "watch_episodes": AnimeWatch.episodes,
        "watch_created": AnimeWatch.created,
        "watch_score": AnimeWatch.score,
        "media_type": Anime.media_type,
        "start_date": Anime.start_date,
        "scored_by": Anime.scored_by,
        "score": Anime.score,
    }

    order_by = [
        (
            desc(order_mapping[field])
            if order == "desc"
            else asc(order_mapping[field])
        )
        for field, order in (entry.split(":") for entry in sort)
    ] + [desc(Anime.content_id)]

    return order_by


# Collections stuff
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


def collection_comments_load_options(query: Select):
    return query.options(
        with_expression(
            Collection.comments_count,
            get_comments_count_subquery(
                Collection.id, constants.CONTENT_COLLECTION
            ),
        )
    )


def collections_load_options(
    query: Select, request_user: User | None, preview: bool = False
):
    # Yeah, I like it but not sure about performance
    query = collection_comments_load_options(
        query.options(
            joinedload(Collection.collection.of_type(AnimeCollectionContent))
            .joinedload(AnimeCollectionContent.content)
            .joinedload(Anime.watch),
            with_loader_criteria(
                AnimeWatch,
                AnimeWatch.user_id == request_user.id if request_user else None,
            ),
        )
    )

    # Here we load user vote score for collection
    query = query.options(
        with_expression(
            Collection.my_score,
            get_my_score_subquery(
                Collection, constants.CONTENT_COLLECTION, request_user
            ),
        )
    )

    if preview:
        query = query.options(
            with_loader_criteria(
                CollectionContent, CollectionContent.order <= 6
            )
        )

    return query


# Vote stuff
def get_my_score_subquery(content_model, content_type, request_user):
    # We use func.sum inside func.coalesce because otherwise it won't work
    return (
        select(func.coalesce(func.sum(Vote.score), 0))
        .filter(
            Vote.user == request_user,
            Vote.content_id == content_model.id,
            Vote.content_type == content_type,
        )
        .scalar_subquery()
    )
