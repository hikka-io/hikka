from sqlalchemy import select, asc, desc, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.sql.selectable import Select
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


async def build_collection_content(
    session: AsyncSession, collection: Collection, args: CollectionArgs
):
    content_model = content_type_to_content_class[args.content_type]

    cache = await session.scalars(
        select(content_model).filter(
            content_model.slug.in_([content.slug for content in args.content])
        )
    )

    content_cache = {content.slug: content.id for content in cache}

    return [
        CollectionContent(
            **{
                "content_id": content_cache[content.slug],
                "content_type": args.content_type,
                "comment": content.comment,
                "collection": collection,
                "label": content.label,
                "order": content.order,
            }
        )
        for content in args.content
    ]


def collections_load_options(query: Select, request_user: User | None):
    # Yeah, I like it but not sure about performance
    return (
        query.options(
            joinedload(Collection.collection.of_type(AnimeCollectionContent))
            .joinedload(AnimeCollectionContent.content)
            .joinedload(Anime.watch),
            with_loader_criteria(
                AnimeWatch,
                AnimeWatch.user_id == request_user.id if request_user else None,
            ),
        )
        .options(
            with_loader_criteria(
                CollectionContent, CollectionContent.order <= 5
            )
        )
        .order_by(desc(Collection.created))
    )


async def count_content(
    session: AsyncSession, content_type: str, slugs: list[str]
) -> int:
    content_model = content_type_to_content_class[content_type]
    return await session.scalar(
        select(func.count(content_model.id)).filter(
            content_model.slug.in_(slugs)
        )
    )


async def get_collections_count(session: AsyncSession) -> int:
    return await session.scalar(
        select(func.count(Collection.id)).filter(
            Collection.private == False,  # noqa: E712
        )
    )


async def get_collections(
    session: AsyncSession, request_user: User | None, limit: int, offset: int
) -> list[Collection]:
    return await session.scalars(
        collections_load_options(
            select(Collection).filter(
                Collection.private == False,  # noqa: E712
            ),
            request_user,
        )
        .limit(limit)
        .offset(offset)
    )


async def get_user_collections_count(session: AsyncSession, user: User) -> int:
    return await session.scalar(
        select(func.count(Collection.id)).filter(Collection.author == user)
    )


async def get_user_collections(
    session: AsyncSession,
    user: User,
    request_user: User,
    limit: int,
    offset: int,
) -> list[Collection]:
    return await session.scalars(
        collections_load_options(
            select(Collection).filter(Collection.author == user),
            request_user,
        )
        .limit(limit)
        .offset(offset)
    )


async def create_collection(
    session: AsyncSession,
    args: CollectionArgs,
    user: User,
):
    now = datetime.utcnow()

    collection = Collection(
        **{
            "content_type": args.content_type,
            "labels_order": args.labels_order,
            "description": args.description,
            "entries": len(args.content),
            "private": args.private,
            "spoiler": args.spoiler,
            "title": args.title,
            "nsfw": args.nsfw,
            "tags": args.tags,
            "author": user,
            "created": now,
            "updated": now,
        }
    )

    collection_content = await build_collection_content(
        session, collection, args
    )

    session.add_all(collection_content)

    await session.commit()

    return collection


async def update_collection(
    session: AsyncSession, collection: Collection, args: CollectionArgs
):
    # Update collection here
    collection.updated = datetime.utcnow()
    collection.content_type = args.content_type
    collection.labels_order = args.labels_order
    collection.description = args.description
    collection.entries = len(args.content)
    collection.private = args.private
    collection.spoiler = args.spoiler
    collection.title = args.title
    collection.nsfw = args.nsfw
    collection.tags = args.tags

    session.add(collection)

    # First we delete old content
    await session.execute(
        delete(CollectionContent).filter(
            CollectionContent.collection == collection
        )
    )

    collection_content = await build_collection_content(
        session, collection, args
    )

    session.add_all(collection_content)

    await session.commit()
    await session.refresh(collection)

    return collection


async def get_collection(session: AsyncSession, reference: UUID):
    return await session.scalar(
        select(Collection).filter(Collection.id == reference)
    )


async def get_collection_display(
    session: AsyncSession, collection: Collection, request_user: User
):
    return await session.scalar(
        collections_load_options(
            select(Collection).filter(Collection.id == collection.id),
            request_user,
        )
    )
