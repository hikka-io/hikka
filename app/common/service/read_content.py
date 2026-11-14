from sqlalchemy import select, desc, func, exists, and_, ScalarResult, Select
from app.common.service.sort import build_read_content_order_by
from sqlalchemy.orm.attributes import InstrumentedAttribute
from app.common.schemas.manga import MangaSearchArgs
from app.common.schemas.novel import NovelSearchArgs
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from app.service import magazines_count
from sqlalchemy.orm import joinedload
from app.service import genres_count
from dataclasses import dataclass
from app.errors import Abort
from app import constants

from app.models import (
    MangaCharacter,
    NovelCharacter,
    MangaAuthor,
    NovelAuthor,
    Character,
    MangaRead,
    NovelRead,
    Magazine,
    Genre,
    Manga,
    Novel,
    User,
)


@dataclass(frozen=True)
class ReadContentModels:
    """Models and names behind content users read (manga and novels)"""

    content: type[Manga | Novel]
    read: type[MangaRead | NovelRead]
    author: type[MangaAuthor | NovelAuthor]
    character: type[MangaCharacter | NovelCharacter]
    character_content: InstrumentedAttribute
    error_scope: str


manga_models = ReadContentModels(
    content=Manga,
    read=MangaRead,
    author=MangaAuthor,
    character=MangaCharacter,
    character_content=MangaCharacter.manga,
    error_scope="manga",
)

novel_models = ReadContentModels(
    content=Novel,
    read=NovelRead,
    author=NovelAuthor,
    character=NovelCharacter,
    character_content=NovelCharacter.novel,
    error_scope="novel",
)

read_content_models = {
    constants.CONTENT_MANGA: manga_models,
    constants.CONTENT_NOVEL: novel_models,
}

ReadContentSearchArgs = MangaSearchArgs | NovelSearchArgs


async def get_read_content_info_by_slug(
    session: AsyncSession, models: ReadContentModels, slug: str
) -> Manga | Novel | None:
    return await session.scalar(
        select(models.content)
        .filter(
            models.content.slug == slug.lower(),
            models.content.deleted == False,  # noqa: E712
        )
        .options(
            joinedload(models.content.authors).joinedload(models.author.person),
            joinedload(models.content.magazines),
            joinedload(models.content.genres),
        )
    )


async def get_read_content_by_slug(
    session: AsyncSession, models: ReadContentModels, slug: str
) -> Manga | Novel | None:
    return await session.scalar(
        select(models.content).filter(
            models.content.slug == slug.lower(),
            models.content.deleted == False,  # noqa: E712
        )
    )


async def validate_read_content_search_args(
    session: AsyncSession,
    models: ReadContentModels,
    search: ReadContentSearchArgs,
):
    # Check if provided magazines exist
    if len(search.magazines) > 0:
        magazines = await magazines_count(session, search.magazines)
        if magazines != len(search.magazines):
            raise Abort(models.error_scope, "unknown-magazine")

    # Check if provided genres exist
    if len(search.genres) > 0:
        genre_names_to_validate = {
            genre[1:] if genre.startswith("-") else genre
            for genre in search.genres
        }

        valid_genres_count = await genres_count(
            session, list(genre_names_to_validate)
        )

        if valid_genres_count != len(genre_names_to_validate):
            raise Abort(models.error_scope, "unknown-genre")


def read_content_search_filter(
    models: ReadContentModels,
    search: ReadContentSearchArgs,
    query: Select,
    hide_nsfw=True,
):
    content = models.content

    # Score filters
    if search.score[0] and search.score[0] > 0:
        query = query.filter(content.score >= search.score[0])

    if search.score[1]:
        query = query.filter(content.score <= search.score[1])

    # Native score filters
    if search.native_score[0] and search.native_score[0] > 0:
        query = query.filter(content.native_score >= search.native_score[0])

    if search.native_score[1]:
        query = query.filter(content.native_score <= search.native_score[1])

    if len(search.status) > 0:
        query = query.filter(content.status.in_(search.status))

    if len(search.media_type) > 0:
        query = query.filter(content.media_type.in_(search.media_type))

    if search.only_translated:
        query = query.filter(content.translated_ua == True)  # noqa: E712

    if search.years[0]:
        query = query.filter(content.year >= search.years[0])

    if search.years[1]:
        query = query.filter(content.year <= search.years[1])

    if len(search.magazines) > 0:
        query = query.filter(
            content.magazines.any(Magazine.slug.in_(search.magazines))
        )

    # In some cases, like on front page, we would want to hide NSFW content
    if len(search.genres) == 0 and hide_nsfw:
        query = query.filter(
            and_(
                *[
                    ~content.genres.any(Genre.slug == slug)
                    for slug in ["ecchi", "erotica", "hentai"]
                ]
            )
        )

    if len(search.genres) > 0:
        include_genres = []
        exclude_genres = []

        for genre_slug in search.genres:
            if genre_slug.startswith("-"):
                exclude_genres.append(genre_slug[1:])
            else:
                include_genres.append(genre_slug)

        if include_genres:
            query = query.filter(
                and_(
                    *[
                        content.genres.any(Genre.slug == slug)
                        for slug in include_genres
                    ]
                )
            )

        if exclude_genres:
            query = query.filter(
                and_(
                    *[
                        ~content.genres.any(Genre.slug == slug)
                        for slug in exclude_genres
                    ]
                )
            )

    return query


def exclude_read_filter(
    models: ReadContentModels,
    search: ReadContentSearchArgs,
    query: Select,
    request_user: User | None,
):
    if not request_user or not search.exclude_read_status:
        return query

    return query.filter(
        ~exists().where(
            models.read.deleted == False,  # noqa: E712
            models.read.status.in_(search.exclude_read_status),
            models.read.user_id == request_user.id,
            models.read.content_id == models.content.id,
        )
    )


async def exclude_read_content_ids(
    session: AsyncSession,
    models: ReadContentModels,
    search: ReadContentSearchArgs,
    request_user: User | None,
) -> list[str]:
    if not request_user or not search.exclude_read_status:
        return []

    content_ids = await session.scalars(
        select(models.content.content_id)
        .join(models.read, models.read.content_id == models.content.id)
        .filter(
            models.read.user_id == request_user.id,
            models.read.status.in_(search.exclude_read_status),
            models.read.deleted == False,  # noqa: E712
        )
    )

    return content_ids.all()


async def read_content_search(
    session: AsyncSession,
    models: ReadContentModels,
    search: ReadContentSearchArgs,
    filter_ids: list[str],
    request_user: User | None,
    limit: int,
    offset: int,
):
    # Load request user read statuses here
    load_options = [
        joinedload(models.content.read),
        with_loader_criteria(
            models.read,
            models.read.user_id == request_user.id if request_user else None,
        ),
    ]

    query = select(models.content).filter(
        models.content.deleted == False  # noqa: E712
    )

    if filter_ids:
        query = query.filter(models.content.content_id.in_(filter_ids))

    # NOTE: we should have dedicated nsfw filter
    # and don't do stupid things like this
    hide_nsfw = len(filter_ids) == 0

    query = read_content_search_filter(models, search, query, hide_nsfw)
    query = exclude_read_filter(models, search, query, request_user)

    query = query.order_by(
        *build_read_content_order_by(models.content, search.sort)
    )

    query = query.options(*load_options)
    query = query.limit(limit).offset(offset)

    return await session.scalars(query)


async def read_content_search_total(
    session: AsyncSession,
    models: ReadContentModels,
    search: ReadContentSearchArgs,
    filter_ids: list[str],
    request_user: User | None,
):
    query = select(func.count(models.content.id)).filter(
        models.content.deleted == False  # noqa: E712
    )

    if filter_ids:
        query = query.filter(models.content.content_id.in_(filter_ids))

    # NOTE: we should have dedicated nsfw filter
    # and don't do stupid things like this
    hide_nsfw = len(filter_ids) == 0

    query = read_content_search_filter(models, search, query, hide_nsfw)
    query = exclude_read_filter(models, search, query, request_user)

    return await session.scalar(query)


async def read_content_characters_count(
    session: AsyncSession, models: ReadContentModels, content: Manga | Novel
) -> int:
    return await session.scalar(
        select(func.count(models.character.id)).filter(
            models.character_content == content
        )
    )


async def read_content_characters(
    session: AsyncSession,
    models: ReadContentModels,
    content: Manga | Novel,
    limit: int,
    offset: int,
) -> ScalarResult[MangaCharacter | NovelCharacter]:
    return await session.scalars(
        select(models.character)
        .join(Character, models.character.character)
        .filter(models.character_content == content)
        .options(joinedload(models.character.character))
        .order_by(
            desc(models.character.main),
            desc(Character.favorites),
            desc(Character.content_id),
        )
        .limit(limit)
        .offset(offset)
    )
