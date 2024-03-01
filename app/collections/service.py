from sqlalchemy import select, desc, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import with_expression
from sqlalchemy.orm import joinedload
from .schemas import CollectionArgs
from datetime import datetime
from app import constants
from uuid import UUID

from app.service import (
    get_comments_count_subquery,
    create_log,
)

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


def collections_load_options(
    query: Select, request_user: User | None, preview: bool = False
):
    # Yeah, I like it but not sure about performance
    query = query.options(
        joinedload(Collection.collection.of_type(AnimeCollectionContent))
        .joinedload(AnimeCollectionContent.content)
        .joinedload(Anime.watch),
        with_loader_criteria(
            AnimeWatch,
            AnimeWatch.user_id == request_user.id if request_user else None,
        ),
    )

    if preview:
        query = query.options(
            with_loader_criteria(
                CollectionContent, CollectionContent.order <= 6
            )
        )

    return query.order_by(desc(Collection.created))


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
            Collection.deleted == False,  # noqa: E712
        )
    )


async def get_collections(
    session: AsyncSession, request_user: User | None, limit: int, offset: int
) -> list[Collection]:
    return await session.scalars(
        collections_load_options(
            select(Collection).filter(
                Collection.private == False,  # noqa: E712
                Collection.deleted == False,  # noqa: E712
            ),
            request_user,
            True,
        )
        .options(
            with_expression(
                Collection.comments_count,
                get_comments_count_subquery(
                    Collection.id, constants.CONTENT_COLLECTION
                ),
            )
        )
        .limit(limit)
        .offset(offset)
    )


async def get_user_collections_count(session: AsyncSession, user: User) -> int:
    return await session.scalar(
        select(func.count(Collection.id)).filter(
            Collection.deleted == False,  # noqa: E712
            Collection.author == user,
        )
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
            select(Collection).filter(
                Collection.deleted == False,  # noqa: E712
                Collection.author == user,
            ),
            request_user,
            True,
        )
        .options(
            with_expression(
                Collection.comments_count,
                get_comments_count_subquery(
                    Collection.id, constants.CONTENT_COLLECTION
                ),
            )
        )
        .limit(limit)
        .offset(offset)
    )


async def get_collection(session: AsyncSession, reference: UUID):
    return await session.scalar(
        select(Collection)
        .filter(
            Collection.deleted == False,  # noqa: E712
            Collection.id == reference,
        )
        .options(
            with_expression(
                Collection.comments_count,
                get_comments_count_subquery(
                    Collection.id, constants.CONTENT_COLLECTION
                ),
            )
        )
    )


async def get_collection_display(
    session: AsyncSession, collection: Collection, request_user: User
):
    return await session.scalar(
        collections_load_options(
            select(Collection).filter(Collection.id == collection.id),
            request_user,
        ).options(
            with_expression(
                Collection.comments_count,
                get_comments_count_subquery(
                    Collection.id, constants.CONTENT_COLLECTION
                ),
            )
        )
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
            "deleted": False,
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

    await create_log(
        session,
        constants.LOG_COLLECTION_CREATE,
        user,
        collection.id,
        {
            "content_type": args.content_type,
            "labels_order": args.labels_order,
            "description": args.description,
            "entries": len(args.content),
            "private": args.private,
            "spoiler": args.spoiler,
            "title": args.title,
            "nsfw": args.nsfw,
            "tags": args.tags,
            "content": [
                {
                    "content_id": str(content.content_id),
                    "content_type": content.content_type,
                    "comment": content.comment,
                    "label": content.label,
                    "order": content.order,
                }
                for content in collection_content
            ],
        },
    )

    return collection


async def update_collection(
    session: AsyncSession,
    collection: Collection,
    args: CollectionArgs,
    user: User,
):
    before = {}
    after = {}

    for key in [
        "labels_order",
        "description",
        "private",
        "spoiler",
        "title",
        "nsfw",
        "tags",
    ]:
        old_value = getattr(collection, key)
        new_value = getattr(args, key)

        if old_value != new_value:
            before[key] = old_value
            setattr(collection, key, new_value)
            after[key] = new_value

    collection.updated = datetime.utcnow()
    session.add(collection)

    if len(args.content) > 0:
        collection_content_old = await session.scalars(
            select(CollectionContent).filter(
                CollectionContent.collection == collection
            )
        )

        collection_content = await build_collection_content(
            session, collection, args
        )

        old_content = [
            {
                "content_id": str(content.content_id),
                "content_type": content.content_type,
                "comment": content.comment,
                "label": content.label,
                "order": content.order,
            }
            for content in collection_content_old
        ]

        new_content = [
            {
                "content_id": str(content.content_id),
                "content_type": content.content_type,
                "comment": content.comment,
                "label": content.label,
                "order": content.order,
            }
            for content in collection_content
        ]

        # Only update collection content if it has changed
        if old_content != new_content:
            # Update collection entries count
            collection.entries = len(args.content)

            # First we delete old content
            await session.execute(
                delete(CollectionContent).filter(
                    CollectionContent.collection == collection
                )
            )

            session.add_all(collection_content)

            await session.commit()
            await session.refresh(collection)

            before["content"] = old_content
            after["content"] = new_content

    if before != {} and after != {}:
        await create_log(
            session,
            constants.LOG_COLLECTION_UPDATE,
            user,
            collection.id,
            {
                "updated_collection": after,
                "old_collection": before,
            },
        )

    return collection


async def delete_collection(
    session: AsyncSession, collection: Collection, user: User
):
    collection.deleted = True

    session.add(collection)
    await session.commit()

    await create_log(
        session,
        constants.LOG_COLLECTION_DELETE,
        user,
        collection.id,
    )

    return True


async def content_compare(
    session: AsyncSession, collection: Collection, args: CollectionArgs
):
    collection_content = await session.scalars(
        select(CollectionContent).filter(
            CollectionContent.collection == collection
        )
    )

    collection_compare = [
        {
            "slug": content.content.slug,
            "comment": content.comment,
            "label": content.label,
            "order": content.order,
        }
        for content in collection_content
    ]

    args_compare = [
        {
            "slug": content.slug,
            "comment": content.comment,
            "label": content.label,
            "order": content.order,
        }
        for content in args.content
    ]

    return collection_compare == args_compare
