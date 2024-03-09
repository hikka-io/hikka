from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.orm import with_expression
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from .schemas import ContentTypeEnum
from datetime import datetime
from app import constants

from app.service import (
    get_comments_count_subquery,
    collections_load_options,
    create_log,
)

from app.models import (
    CollectionFavourite,
    AnimeFavourite,
    AnimeWatch,
    Collection,
    Favourite,
    Anime,
    User,
)


content_type_to_favourite_class = {
    constants.CONTENT_COLLECTION: CollectionFavourite,
    constants.CONTENT_ANIME: AnimeFavourite,
}


async def get_favourite(
    session: AsyncSession,
    content_type: ContentTypeEnum,
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
    content_type: ContentTypeEnum,
    content: Anime,
    user: User,
) -> Favourite:
    favourite_model = content_type_to_favourite_class[content_type]

    favourite = favourite_model(
        **{
            "created": datetime.utcnow(),
            "content_id": content.id,
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
    content_type: ContentTypeEnum,
    user: User,
    request_user: User | None,
    limit: int,
    offset: int,
) -> list[Favourite]:
    favourite_model = content_type_to_favourite_class[content_type]

    if content_type == constants.CONTENT_ANIME:
        query = (
            select(Anime)
            .join(
                favourite_model,
                favourite_model.content_id == Anime.id,
            )
            .filter(favourite_model.user == user)
            .options(
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
            .options(
                with_expression(
                    Anime.favourite_created,
                    favourite_model.created,
                )
            )
        )

    if content_type == constants.CONTENT_COLLECTION:
        query = (
            collections_load_options(
                select(Collection).filter(
                    Collection.private == False,  # noqa: E712
                    Collection.deleted == False,  # noqa: E712
                ),
                request_user,
                True,
            )
            .join(
                favourite_model,
                favourite_model.content_id == Collection.id,
            )
            .options(
                with_expression(
                    Collection.comments_count,
                    get_comments_count_subquery(
                        Collection.id, constants.CONTENT_COLLECTION
                    ),
                )
            )
            .options(
                with_expression(
                    Collection.favourite_created,
                    favourite_model.created,
                )
            )
        )

    return await session.scalars(
        query.order_by(desc(favourite_model.created))
        .limit(limit)
        .offset(offset)
    )


async def get_user_favourite_list_count(
    session: AsyncSession,
    content_type: ContentTypeEnum,
    user: User,
) -> int:
    favourite_model = content_type_to_favourite_class[content_type]
    return await session.scalar(
        select(func.count(favourite_model.id)).filter(
            favourite_model.user == user
        )
    )
