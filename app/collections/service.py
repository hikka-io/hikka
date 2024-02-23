from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy import select, asc, func
from app.service import anime_loadonly
from sqlalchemy.orm import joinedload
from .schemas import CollectionArgs
from datetime import datetime
from app import constants
from uuid import UUID

from app.models import (
    CharacterCollectionContent,
    PersonCollectionContent,
    AnimeCollectionContent,
    CollectionContent,
    AnimeWatch,
    Collection,
    Character,
    Person,
    Anime,
    User,
)


content_type_to_content_class = {
    constants.CONTENT_CHARACTER: Character,
    constants.CONTENT_PERSON: Person,
    constants.CONTENT_ANIME: Anime,
}


content_type_to_collection_content_class = {
    constants.CONTENT_CHARACTER: CharacterCollectionContent,
    constants.CONTENT_PERSON: PersonCollectionContent,
    constants.CONTENT_ANIME: AnimeCollectionContent,
}


async def count_content(
    session: AsyncSession, content_type: str, slugs: list[str]
) -> int:
    content_model = content_type_to_content_class[content_type]
    return await session.scalar(
        select(func.count(content_model.id)).filter(
            content_model.slug.in_(slugs)
        )
    )


async def get_user_collections_count(session: AsyncSession, user: User) -> int:
    return await session.scalar(
        select(func.count(Collection.id)).filter(Collection.author == user)
    )


async def get_user_collections(
    session: AsyncSession, user: User, limit: int, offset: int
) -> list[Collection]:
    return await session.scalars(
        select(Collection)
        .filter(Collection.author == user)
        .limit(limit)
        .offset(offset)
    )


async def create_collection(
    session: AsyncSession,
    args: CollectionArgs,
    user: User,
):
    now = datetime.utcnow()
    content_model = content_type_to_content_class[args.content_type]

    cache = await session.scalars(
        select(content_model).filter(
            content_model.slug.in_([content.slug for content in args.content])
        )
    )

    content_cache = {content.slug: content.id for content in cache}

    collection = Collection(
        **{
            "content_type": args.content_type,
            "labels_order": args.labels_order,
            "description": args.description,
            "entries": len(args.content),
            "spoiler": args.spoiler,
            "title": args.title,
            "nsfw": args.nsfw,
            "author": user,
            "created": now,
            "updated": now,
        }
    )

    session.add(collection)

    for content in args.content:
        collection_content = CollectionContent(
            **{
                "content_id": content_cache[content.slug],
                "content_type": args.content_type,
                "comment": content.comment,
                "collection": collection,
                "label": content.label,
                "order": content.order,
            }
        )

        session.add(collection_content)

    await session.commit()

    return collection


async def get_collection(session: AsyncSession, reference: UUID):
    return await session.scalar(
        select(Collection).filter(Collection.id == reference)
    )


async def get_collection_display(
    session: AsyncSession, reference: UUID, request_user: User
):
    # ToDo: refactor this function (I hate this abomination)
    # Note: Ideally this should be single request to database
    collection = await get_collection(session, reference)

    # I hate long variable names
    content_model = content_type_to_collection_content_class[
        collection.content_type
    ]

    # By default we only load collection content
    load_options = [joinedload(content_model.content)]

    # Special case for anime
    # Only reason to have this attrocity is because
    # we must return user watch status.
    if collection.content_type == constants.CONTENT_ANIME:
        load_options = [
            anime_loadonly(joinedload(content_model.content)).joinedload(
                Anime.watch
            ),
            with_loader_criteria(
                AnimeWatch,
                AnimeWatch.user_id == request_user.id if request_user else None,
            ),
        ]

    # Load content
    content = await session.scalars(
        select(content_model)
        .filter(collection == collection)
        .options(*load_options)
        .order_by(asc(content_model.order))
    )

    # The lengths we go for better user experience...
    return {
        "description": collection.description,
        "reference": collection.reference,
        "spoiler": collection.spoiler,
        "entries": collection.entries,
        "created": collection.created,
        "updated": collection.updated,
        "author": collection.author,
        "title": collection.title,
        "nsfw": collection.nsfw,
        "content": content.unique().all(),
    }
