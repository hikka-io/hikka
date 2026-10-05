from app.common.service.collections import collection_member_exists
from app.common.service.collections import collections_load_options
from app.common.service.collections import get_collection_member
from .schemas import CollectionsListArgs, CollectionArgs
from app.service import content_type_to_content_class
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import aliased
from .utils import member_log_data
from app.utils import utcnow
from app import constants
from uuid import UUID

from app.service import (
    get_followed_user_ids,
    get_user_by_username,
    create_log,
)

from sqlalchemy import (
    ScalarResult,
    select,
    delete,
    update,
    func,
    case,
    desc,
    and_,
    asc,
    or_,
)

from app.models import (
    CharacterCollectionContent,
    PersonCollectionContent,
    AnimeCollectionContent,
    MangaCollectionContent,
    NovelCollectionContent,
    CollectionContent,
    CollectionComment,
    CollectionMember,
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
        query = query.filter(collection_member_exists(author.id))

        # Private collections can be seen only on per user basis
        if author == request_user:
            visibility.append(constants.COLLECTION_PRIVATE)

    if args.content_type:
        query = query.filter(Collection.content_type == args.content_type)

    if len(args.tags) > 0:
        query = query.filter(
            and_(*[Collection.tags.any(name) for name in args.tags])
        )

    if args.only_public:
        visibility = [constants.COLLECTION_PUBLIC]

    # Here we look up for collections with specified content present
    if len(args.content) > 0:
        # Get content model and fetch content ids for provided slugs
        content_model = content_type_to_content_class[args.content_type]
        content_ids = (
            await session.scalars(
                select(content_model.id).filter(
                    content_model.slug.in_(args.content)
                )
            )
        ).all()

        for content_id in content_ids:
            content_alias = aliased(CollectionContent)
            query = query.join(
                content_alias,
                and_(
                    content_alias.collection_id == Collection.id,
                    content_alias.content_id == content_id,
                ),
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
) -> ScalarResult[Collection]:
    followed_user_ids = await get_followed_user_ids(session, request_user)

    query = await collections_list_filter(
        collections_load_options(
            select(Collection).options(
                joinedload(Collection.author).with_expression(
                    User.is_followed,
                    case((User.id.in_(followed_user_ids), True), else_=False),
                )
            ),
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
    # Counted by ownership, not by author_id: a transferred collection must
    # count against its new owner, otherwise transfer would be a way to
    # launder the quota. Being invited as a co-author costs nothing
    return await session.scalar(
        select(func.count(Collection.id))
        .join(
            CollectionMember,
            CollectionMember.collection_id == Collection.id,
        )
        .filter(
            Collection.deleted == False,  # noqa: E712
            CollectionMember.user_id == user.id,
            CollectionMember.role == constants.COLLECTION_MEMBER_OWNER,
            CollectionMember.status == constants.COLLECTION_MEMBER_ACCEPTED,
        )
    )


async def get_collection(
    session: AsyncSession,
    reference: UUID,
    request_user: User,
):
    collection = await session.scalar(
        select(Collection)
        .options(joinedload(Collection.author))
        .filter(
            Collection.deleted == False,  # noqa: E712
            Collection.id == reference,
        ),
    )

    if collection is None:
        return None

    # Short circuit: non private collections need no membership lookup
    if collection.visibility != constants.COLLECTION_PRIVATE:
        return collection

    # Private collections are visible to members only. Pending invitees
    # are let in read only, so they can see what they are invited to and
    # accept or decline; every write path checks accepted membership on
    # its own. Note that author_id grants nothing here, a creator who
    # left the collection can no longer see it
    if not await get_collection_member(
        session, collection.id, request_user, status=None
    ):
        return None

    return collection


async def get_collection_display(
    session: AsyncSession, collection: Collection, request_user: User
):
    followed_user_ids = await get_followed_user_ids(session, request_user)

    query = (
        select(Collection)
        .options(
            joinedload(Collection.author).with_expression(
                User.is_followed,
                case((User.id.in_(followed_user_ids), True), else_=False),
            )
        )
        .filter(Collection.id == collection.id)
    )

    return await session.scalar(collections_load_options(query, request_user))


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

    # Author becomes the owner. Permissions live here, not in author_id,
    # which stays as a record of who created the collection
    session.add(
        CollectionMember(
            **{
                "status": constants.COLLECTION_MEMBER_ACCEPTED,
                "role": constants.COLLECTION_MEMBER_OWNER,
                "collection": collection,
                "invited_by": None,
                "created": now,
                "updated": now,
                "user": user,
            }
        )
    )

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
        private = collection.visibility == constants.COLLECTION_PRIVATE

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


async def count_collection_members(
    session: AsyncSession, collection: Collection
) -> int:
    """
    Members of a collection excluding its owner

    Counts pending invites too, so that outstanding invites can't push the
    collection past the co-author limit once accepted.
    """

    return await session.scalar(
        select(func.count(CollectionMember.id)).filter(
            CollectionMember.collection_id == collection.id,
            CollectionMember.role != constants.COLLECTION_MEMBER_OWNER,
        )
    )


async def count_user_pending_invites(
    session: AsyncSession, user: User
) -> int:
    """Pending invites waiting for the user across all collections"""

    return await session.scalar(
        select(func.count(CollectionMember.id)).filter(
            CollectionMember.user_id == user.id,
            CollectionMember.status == constants.COLLECTION_MEMBER_PENDING,
        )
    )


def collection_members_load_options(query: Select):
    return query.options(
        joinedload(CollectionMember.invited_by),
        joinedload(CollectionMember.user),
    )


def collection_members_filter(
    query: Select,
    collection: Collection,
    request_user: User | None,
    is_owner: bool,
):
    query = query.filter(CollectionMember.collection_id == collection.id)

    # Who was invited is not public information: pending rows are visible
    # to the owner and to the invited user only
    if not is_owner:
        visible = (
            CollectionMember.status == constants.COLLECTION_MEMBER_ACCEPTED
        )

        if request_user:
            visible = or_(
                visible, CollectionMember.user_id == request_user.id
            )

        query = query.filter(visible)

    return query


async def get_collection_members_count(
    session: AsyncSession,
    collection: Collection,
    request_user: User | None,
    is_owner: bool,
) -> int:
    # NOTE: same filter as the list query on purpose, otherwise the total
    # would leak how many invites are pending
    query = collection_members_filter(
        select(func.count(CollectionMember.id)),
        collection,
        request_user,
        is_owner,
    )

    return await session.scalar(query)


async def get_collection_members(
    session: AsyncSession,
    collection: Collection,
    request_user: User | None,
    is_owner: bool,
    limit: int,
    offset: int,
) -> ScalarResult[CollectionMember]:
    query = collection_members_filter(
        select(CollectionMember), collection, request_user, is_owner
    )

    return await session.scalars(
        collection_members_load_options(query)
        # Owner first, and they are not necessarily the oldest row:
        # after a transfer the previous owner's row is older
        .order_by(
            case(
                (
                    CollectionMember.role
                    == constants.COLLECTION_MEMBER_OWNER,
                    0,
                ),
                else_=1,
            ),
            asc(CollectionMember.created),
        )
        .limit(limit)
        .offset(offset)
    )


async def invite_collection_member(
    session: AsyncSession,
    collection: Collection,
    member_user: User,
    user: User,
) -> CollectionMember:
    now = utcnow()

    member = CollectionMember(
        **{
            "status": constants.COLLECTION_MEMBER_PENDING,
            "role": constants.COLLECTION_MEMBER_EDITOR,
            "collection": collection,
            "user": member_user,
            "created": now,
            "updated": now,
            "invited_by": user,
        }
    )

    session.add(member)
    await session.commit()

    await create_log(
        session,
        constants.LOG_COLLECTION_MEMBER_INVITE,
        user,
        collection.id,
        member_log_data(member_user),
    )

    return member


async def accept_collection_invite(
    session: AsyncSession,
    collection: Collection,
    member: CollectionMember,
    user: User,
) -> CollectionMember:
    member.status = constants.COLLECTION_MEMBER_ACCEPTED
    member.updated = utcnow()

    session.add(member)
    await session.commit()

    await create_log(
        session,
        constants.LOG_COLLECTION_MEMBER_ACCEPT,
        user,
        collection.id,
        member_log_data(user),
    )

    return member


async def delete_collection_member(
    session: AsyncSession,
    collection: Collection,
    member: CollectionMember,
    user: User,
) -> bool:
    member_user = member.user
    pending = member.status == constants.COLLECTION_MEMBER_PENDING

    # Declining an invite and walking out of a collection are different
    # intents, and only the first one puts the inviter on cooldown
    if member.user_id != user.id:
        log_type = constants.LOG_COLLECTION_MEMBER_REMOVE
    elif pending:
        log_type = constants.LOG_COLLECTION_MEMBER_DECLINE
    else:
        log_type = constants.LOG_COLLECTION_MEMBER_LEAVE

    # Hard delete, the log is the history here
    await session.delete(member)
    await session.commit()

    await create_log(
        session,
        log_type,
        user,
        collection.id,
        member_log_data(member_user),
    )

    return True


async def get_collection_owner_offer(
    session: AsyncSession, collection: Collection
) -> CollectionMember | None:
    return await session.scalar(
        select(CollectionMember)
        .options(joinedload(CollectionMember.user))
        .filter(
            CollectionMember.collection_id == collection.id,
            CollectionMember.owner_offered_at.is_not(None),
        )
    )


async def offer_collection_ownership(
    session: AsyncSession,
    collection: Collection,
    member: CollectionMember,
    user: User,
) -> CollectionMember:
    member.owner_offered_at = utcnow()
    member.updated = member.owner_offered_at

    session.add(member)
    await session.commit()

    await create_log(
        session,
        constants.LOG_COLLECTION_OWNER_OFFER,
        user,
        collection.id,
        member_log_data(member.user),
    )

    return member


async def cancel_collection_ownership_offer(
    session: AsyncSession,
    collection: Collection,
    offer: CollectionMember,
    user: User,
) -> bool:
    # Rights are untouched by this: the member stays an accepted editor
    # throughout, the offer only ever lived in owner_offered_at
    offer.owner_offered_at = None
    offer.updated = utcnow()

    session.add(offer)
    await session.commit()

    await create_log(
        session,
        constants.LOG_COLLECTION_OWNER_CANCEL,
        user,
        collection.id,
        member_log_data(offer.user),
    )

    return True


async def accept_collection_ownership(
    session: AsyncSession,
    collection: Collection,
    offer: CollectionMember,
    user: User,
) -> bool:
    # Lock the owner row so two concurrent transfers can't both demote it
    # and then fight over the partial unique index
    owner_member = await session.scalar(
        select(CollectionMember)
        .filter(
            CollectionMember.collection_id == collection.id,
            CollectionMember.role == constants.COLLECTION_MEMBER_OWNER,
        )
        .with_for_update()
    )

    # Always found: an offer can only be made by the owner, and an owner
    # row never goes away on its own, only with the whole collection
    assert owner_member is not None

    now = utcnow()

    # Order matters: a collection may never have two owners, and unique
    # indexes in Postgres can't be deferred. Core statements because the
    # ORM orders flushed updates by identity map, not by assignment
    await session.execute(
        update(CollectionMember)
        .filter(CollectionMember.id == owner_member.id)
        .values(role=constants.COLLECTION_MEMBER_EDITOR, updated=now)
    )
    await session.execute(
        update(CollectionMember)
        .filter(CollectionMember.id == offer.id)
        .values(
            role=constants.COLLECTION_MEMBER_OWNER,
            owner_offered_at=None,
            updated=now,
        )
    )

    # NOTE: create_log commits, so it must run after both updates are in.
    # Logging between them would commit an ownerless collection
    await session.commit()

    await create_log(
        session,
        constants.LOG_COLLECTION_OWNER_TRANSFER,
        user,
        collection.id,
        member_log_data(user),
    )

    return True

