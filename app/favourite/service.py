from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from .schemas import FavouriteContentTypeEnum
from sqlalchemy.orm import with_expression
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from app.utils import utcnow
from app import constants

from app.service import (
    content_type_to_content_class,
    collections_load_options,
    create_log,
)

from app.models import (
    CollectionFavourite,
    CharacterFavourite,
    AnimeFavourite,
    MangaFavourite,
    NovelFavourite,
    AnimeWatch,
    Collection,
    Favourite,
    MangaRead,
    NovelRead,
    Anime,
    Manga,
    Novel,
    User,
)


content_type_to_favourite_class = {
    constants.CONTENT_COLLECTION: CollectionFavourite,
    constants.CONTENT_CHARACTER: CharacterFavourite,
    constants.CONTENT_ANIME: AnimeFavourite,
    constants.CONTENT_MANGA: MangaFavourite,
    constants.CONTENT_NOVEL: NovelFavourite,
}


async def get_favourite(
    session: AsyncSession,
    content_type: FavouriteContentTypeEnum,
    content: Anime,
    user: User,
) -> Favourite | None:
    favourite_model = content_type_to_favourite_class[content_type]
    return await session.scalar(
        select(favourite_model).filter(
            favourite_model.content_id == content.id,
            favourite_model.user == user,
        )
    )


async def create_favourite(
    session: AsyncSession,
    content_type: FavouriteContentTypeEnum,
    content: Anime,
    user: User,
) -> Favourite:
    favourite_model = content_type_to_favourite_class[content_type]

    favourite = favourite_model(
        **{
            "content_id": content.id,
            "created": utcnow(),
            "user": user,
        }
    )

    session.add(favourite)
    await session.commit()

    await create_log(
        session,
        constants.LOG_FAVOURITE,
        user,
        content.id,
        {"content_type": content_type},
    )

    return favourite


async def delete_favourite(session: AsyncSession, favourite: Favourite):
    await session.delete(favourite)
    await session.commit()

    await create_log(
        session,
        constants.LOG_FAVOURITE_REMOVE,
        favourite.user,
        favourite.content_id,
        {"content_type": favourite.content_type},
    )


async def get_user_favourite_list(
    session: AsyncSession,
    content_type: FavouriteContentTypeEnum,
    user: User,
    request_user: User | None,
    limit: int,
    offset: int,
) -> list[Favourite]:
    # At some point I decided that best approach for favourite would be
    # to return list of content with some extra metadata (created/order)
    # instead of returning list of favourite entries with content loaded.
    # Some parts of it way to hackish for my taste so eventually this
    # should be rewritten into something better.
    # (Who am I lying to? This piece of code will stay here forever xD).

    favourite_model = content_type_to_favourite_class[content_type]
    content_model = content_type_to_content_class[content_type]

    query = (
        select(content_model)
        .join(
            favourite_model,
            favourite_model.content_id == content_model.id,
        )
        .filter(favourite_model.user == user)
    )

    if content_type == constants.CONTENT_ANIME:
        query = query.filter(
            content_model.deleted == False,  # noqa: E712
        )

        query = query.options(
            joinedload(Anime.watch),
            with_loader_criteria(
                AnimeWatch,
                (
                    AnimeWatch.user_id == request_user.id
                    if request_user
                    else None
                ),
            ),
        )

    if content_type == constants.CONTENT_MANGA:
        query = query.filter(
            content_model.deleted == False,  # noqa: E712
        )

        query = query.options(
            joinedload(Manga.read),
            with_loader_criteria(
                MangaRead,
                (
                    MangaRead.user_id == request_user.id
                    if request_user
                    else None
                ),
            ),
        )

    if content_type == constants.CONTENT_NOVEL:
        query = query.filter(
            content_model.deleted == False,  # noqa: E712
        )

        query = query.options(
            joinedload(Novel.read),
            with_loader_criteria(
                NovelRead,
                (
                    NovelRead.user_id == request_user.id
                    if request_user
                    else None
                ),
            ),
        )

    if content_type == constants.CONTENT_COLLECTION:
        query = query.filter(
            Collection.deleted == False,  # noqa: E712
        )

        if request_user != user:
            query = query.filter(
                Collection.visibility.in_(
                    [constants.COLLECTION_PUBLIC, constants.COLLECTION_UNLISTED]
                )
            )

        query = collections_load_options(query, request_user, True)

    return await session.scalars(
        query.options(
            with_expression(
                content_model.favourite_created,
                favourite_model.created,
            )
        )
        .order_by(desc(favourite_model.created))
        .limit(limit)
        .offset(offset)
    )


async def get_user_favourite_list_count(
    session: AsyncSession,
    content_type: FavouriteContentTypeEnum,
    user: User,
    request_user: User,
) -> int:
    favourite_model = content_type_to_favourite_class[content_type]
    content_model = content_type_to_content_class[content_type]

    query = (
        select(func.count(content_model.id))
        .join(
            favourite_model,
            favourite_model.content_id == content_model.id,
        )
        .filter(favourite_model.user == user)
    )

    if content_type == constants.CONTENT_ANIME:
        query = query.filter(
            content_model.deleted == False,  # noqa: E712
        )

    if content_type == constants.CONTENT_COLLECTION and request_user != user:
        query = query.filter(
            Collection.visibility.in_(
                [constants.COLLECTION_PUBLIC, constants.COLLECTION_UNLISTED]
            )
        )

    return await session.scalar(query)
