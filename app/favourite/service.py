from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from .schemas import ContentTypeEnum
from datetime import datetime
from app import constants

from app.service import (
    anime_loadonly,
    create_log,
)

from app.models import (
    AnimeFavourite,
    AnimeWatch,
    Favourite,
    Anime,
    User,
)


content_type_to_favourite_class = {
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

    # ToDo: fix old logs (?)
    # await create_log(
    #     session,
    #     constants.LOG_FAVOURITE_ANIME,
    #     user,
    #     anime.id,
    # )

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

    # ToDo: fix old logs (?)
    # await create_log(
    #     session,
    #     constants.LOG_FAVOURITE_ANIME_REMOVE,
    #     favourite.user,
    #     favourite.anime.id,
    # )

    await create_log(
        session,
        constants.LOG_FAVOURITE_REMOVE,
        favourite.user,
        favourite.content_id,
        {"content_type": favourite.content_type},
    )


async def get_user_favourite_list(
    session: AsyncSession,
    user: User,
    request_user: User | None,
    limit: int,
    offset: int,
) -> list[Favourite]:
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
