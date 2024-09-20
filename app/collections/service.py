from sqlalchemy import select, desc, asc, delete, update, and_, func
from app.service import content_type_to_content_class
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from app.utils import utcnow
from app import constants
from uuid import UUID

from .schemas import (
    CollectionsListArgs,
    CollectionArgs,
)

from app.service import (
    collection_comments_load_options,
    collections_load_options,
    get_user_by_username,
    create_log,
)

from app.models import (
    CharacterCollectionContent,
    PersonCollectionContent,
    AnimeCollectionContent,
    MangaCollectionContent,
    NovelCollectionContent,
    CollectionContent,
    CollectionComment,
    Collection,
    User,
)


content_type_to_collection_content_class = {
    constants.CONTENT_CHARACTER: CharacterCollectionContent,
    constants.CONTENT_PERSON: PersonCollectionContent,
    constants.CONTENT_ANIME: AnimeCollectionContent,
    constants.CONTENT_MANGA: MangaCollectionContent,
    constants.CONTENT_NOVEL: NovelCollectionContent,
}


def build_collection_order_by(sort: list[str]):
    order_mapping = {
        "system_ranking": Collection.system_ranking,
        "created": Collection.created,
    }

    order_by = [
        (
            desc(order_mapping[field])
            if order == "desc"
            else asc(order_mapping[field])
        )
        for field, order in (entry.split(":") for entry in sort)
    ]

    return order_by


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


async def count_content(
    session: AsyncSession, content_type: str, slugs: list[str]
) -> int:
    content_model = content_type_to_content_class[content_type]
    return await session.scalar(
        select(func.count(content_model.id)).filter(
            content_model.slug.in_(slugs)
        )
    )


async def collections_list_filter(
    query: Select,
    request_user: User | None,
    args: CollectionsListArgs,
    session: AsyncSession,
):
    visibility = [constants.COLLECTION_PUBLIC, constants.COLLECTION_UNLISTED]

    if args.author:
        author = await get_user_by_username(session, args.author)
        query = query.filter(Collection.author == author)

        # Private collections can be seen only on per user basis
        if author == request_user:
            visibility.append(constants.COLLECTION_PRIVATE)

    if args.content_type:
        query = query.filter(Collection.content_type == args.content_type)

    if args.only_public:
        visibility = [constants.COLLECTION_PUBLIC]

    # Here we look up for collections with specified content present
    if len(args.content) > 0:
        # Get content model and fetch content ids for provided slugs
        content_model = content_type_to_content_class[args.content_type]
        content_ids = await session.scalars(
            select(content_model.id).filter(
                content_model.slug.in_(args.content)
            )
        )

        # Here we use similar logic to anime genres filter
        query = query.join(CollectionContent).filter(
            and_(
                *[
                    CollectionContent.content_id == content_id
                    for content_id in content_ids
                ]
            )
        )

    query = query.filter(
        Collection.visibility.in_(visibility),
        Collection.deleted == False,  # noqa: E712
    )

    return query


async def get_collections_count(
    session: AsyncSession, request_user: User | None, args: CollectionsListArgs
) -> int:
    query = await collections_list_filter(
        select(func.count(Collection.id)), request_user, args, session
    )

    return await session.scalar(query)


async def get_collections(
    session: AsyncSession,
    request_user: User | None,
    args: CollectionsListArgs,
    limit: int,
    offset: int,
) -> list[Collection]:
    query = await collections_list_filter(
        collections_load_options(
            select(Collection),
            request_user,
            True,
        ),
        request_user,
        args,
        session,
    )

    return await session.scalars(
        query.order_by(*build_collection_order_by(args.sort))
        .limit(limit)
        .offset(offset)
    )


async def get_user_collections_count_all(
    session: AsyncSession, user: User
) -> int:
    return await session.scalar(
        select(func.count(Collection.id)).filter(
            Collection.deleted == False,  # noqa: E712
            Collection.author == user,
        )
    )


async def get_collection(
    session: AsyncSession,
    reference: UUID,
    request_user: User,
):
    collection = await session.scalar(
        collection_comments_load_options(
            select(Collection).filter(
                Collection.deleted == False,  # noqa: E712
                Collection.id == reference,
            )
        )
    )

    if (
        collection is not None
        and collection.author != request_user
        and collection.visibility == constants.COLLECTION_PRIVATE
    ):
        return None

    return collection


async def get_collection_display(
    session: AsyncSession, collection: Collection, request_user: User
):
    query = select(Collection).filter(Collection.id == collection.id)
    return await session.scalar(
        collections_load_options(query, request_user).order_by(
            desc(Collection.created)
        )
    )


async def create_collection(
    session: AsyncSession,
    args: CollectionArgs,
    user: User,
):
    now = utcnow()

    collection = Collection(
        **{
            "content_type": args.content_type,
            "labels_order": args.labels_order,
            "description": args.description,
            "visibility": args.visibility,
            "entries": len(args.content),
            "spoiler": args.spoiler,
            "title": args.title,
            "nsfw": args.nsfw,
            "tags": args.tags,
            "deleted": False,
            "vote_score": 0,
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
            "visibility": args.visibility,
            "entries": len(args.content),
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
        "visibility",
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

    collection.updated = utcnow()
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

    # Collection visibility has changed
    # We need to update collection comments private status
    if "visibility" in after:
        private = (
            True
            if collection.visibility == constants.COLLECTION_PRIVATE
            else False
        )

        await session.execute(
            update(CollectionComment)
            .filter(CollectionComment.content == collection)
            .values(private=private)
        )

    await session.commit()
    await session.refresh(collection)

    return collection


async def delete_collection(
    session: AsyncSession, collection: Collection, user: User
):
    collection.deleted = True
    session.add(collection)

    # Mark comments for deleted collection as private
    await session.execute(
        update(CollectionComment)
        .filter(CollectionComment.content == collection)
        .values(private=True)
    )

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
