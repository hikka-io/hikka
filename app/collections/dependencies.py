from app.models import CollectionMember, Collection, User
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from .utils import check_consecutive
from datetime import timedelta
from app.errors import Abort
from fastapi import Depends
from app import constants
from uuid import UUID
from . import service

from app.common.service.collections import (
    get_collection_member,
    is_collection_owner,
)

from app.dependencies import (
    auth_required,
    get_user,
)

from app.utils import (
    check_user_permissions,
    round_datetime,
    to_timestamp,
    utcnow,
)

from app.service import (
    get_user_by_username,
    count_logs,
)

from .schemas import (
    CollectionsListArgs,
    CollectionArgs,
)


async def validate_collections_list_args(
    args: CollectionsListArgs,
    session: AsyncSession = Depends(get_session),
):
    if args.author and not await get_user_by_username(session, args.author):
        raise Abort("collections", "author-not-found")

    if len(args.content) > 0:
        if not args.content_type:
            raise Abort("collections", "empty-content-type")

        # Make sure all provided content do exist in our catabase
        if len(args.content) != await service.count_content(
            session, args.content_type, args.content
        ):
            raise Abort("collections", "bad-content")

    return args


async def validate_collection_args(
    args: CollectionArgs,
    session: AsyncSession = Depends(get_session),
):
    unlabeled_content = False
    labels = set()
    orders = []
    slugs = []

    for content in args.content:
        orders.append(content.order)
        slugs.append(content.slug)

        if not content.label:
            unlabeled_content = True

        else:
            labels.add(content.label)

    if len(labels) > 0 and unlabeled_content:
        raise Abort("collections", "unlabeled-content")

    if len(args.labels_order) != len(labels):
        raise Abort("collections", "bad-labels-order")

    # Make sure all labels from content present in labels_order
    if not all(label in labels for label in args.labels_order):
        raise Abort("collections", "bad-label")

    # Make sure there are no duplicated orders
    if len(list(set(orders))) != len(orders):
        raise Abort("collections", "bad-order-duplicated")

    # Limit number of content in collection
    if len(args.content) < 1 or len(args.content) > 500:
        raise Abort("collections", "content-limit")

    # Order should start from 1
    if sorted(orders)[0] != 1:
        raise Abort("collections", "bad-order-start")

    # Order must be consecutive
    if not check_consecutive(orders):
        raise Abort("collections", "bad-order-not-consecutive")

    content_count = await service.count_content(
        session, args.content_type, slugs
    )

    if content_count != len(slugs):
        raise Abort("collections", "bad-content")

    return args


async def validate_collection_create(
    args: CollectionArgs = Depends(validate_collection_args),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required()),
):
    collections_count = await service.get_user_collections_count_all(
        session, user
    )

    if collections_count >= 1000:
        raise Abort("collections", "limit")

    return args


async def validate_collection(
    reference: UUID,
    request_user: User | None = Depends(auth_required(optional=True)),
    session: AsyncSession = Depends(get_session),
) -> Collection:
    if not (
        collection := await service.get_collection(
            session, reference, request_user
        )
    ):
        raise Abort("collections", "not-found")

    return collection


def check_collection_not_outdated(
    collection: Collection, args: CollectionArgs
):
    # Optimistic locking, requests without updated skip the check
    if args.updated is not None and args.updated != to_timestamp(
        collection.updated
    ):
        raise Abort("collections", "outdated")


async def check_hourly_rate_limit(
    session: AsyncSession,
    user: User,
    log_type: str,
    limit: int,
    inclusive: bool = False,
):
    if user.role in [constants.ROLE_ADMIN, constants.ROLE_MODERATOR]:
        return

    logs_count = await count_logs(
        session,
        log_type,
        user,
        start_time=round_datetime(utcnow(), minutes=60, seconds=60),
    )

    if logs_count >= limit if inclusive else logs_count > limit:
        raise Abort("system", "rate-limit")


async def require_collection_owner(
    session: AsyncSession, collection: Collection, user: User
):
    if not await is_collection_owner(session, collection.id, user):
        raise Abort("collections", "owner-only")


async def get_collection_member_or_abort(
    session: AsyncSession, collection: Collection, user: User
) -> CollectionMember:
    member = await get_collection_member(
        session, collection.id, user, status=None
    )

    if not member:
        raise Abort("collections", "member-not-found")

    return member


async def get_member_user(
    username: str, session: AsyncSession = Depends(get_session)
) -> User:
    """
    Resolve a collection member by username, deleted accounts included

    Unlike app.dependencies.get_user this does not reject deleted users:
    their membership rows outlive the account, and the owner must still be
    able to remove them instead of having them occupy a member slot
    forever.
    """

    if not (user := await get_user_by_username(session, username)):
        raise Abort("user", "not-found")

    return user


async def validate_collection_update(
    args: CollectionArgs = Depends(validate_collection_args),
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required()),
):
    if collection.content_type != args.content_type:
        raise Abort("collections", "bad-content-type")

    check_collection_not_outdated(collection, args)

    member = await get_collection_member(session, collection.id, user)

    if member:
        if (
            member.role != constants.COLLECTION_MEMBER_OWNER
            and args.visibility != collection.visibility
        ):
            raise Abort("collections", "visibility-owner-only")

    else:
        if collection.visibility == constants.COLLECTION_PRIVATE or (
            not check_user_permissions(
                user, [constants.PERMISSION_COLLECTION_UPDATE_MODERATOR]
            )
        ):
            raise Abort("permission", "denied")

        if collection.labels_order != args.labels_order:
            raise Abort("collections", "moderator-content-update")

        if not await service.content_compare(session, collection, args):
            raise Abort("collections", "moderator-content-update")

    await check_hourly_rate_limit(
        session,
        user,
        constants.LOG_COLLECTION_UPDATE,
        constants.COLLECTION_UPDATES_RATE_LIMIT,
    )

    return args


async def validate_collection_delete(
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required()),
):
    # Co-authors can edit but never delete, that stays with the owner.
    # Same as update: moderation never reaches private collections
    if not await is_collection_owner(session, collection.id, user) and (
        collection.visibility == constants.COLLECTION_PRIVATE
        or not check_user_permissions(
            user, [constants.PERMISSION_COLLECTION_DELETE_MODERATOR]
        )
    ):
        raise Abort("permission", "denied")

    return collection


async def validate_collection_owner(
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required(forbid_thirdparty=True)),
) -> Collection:
    await require_collection_owner(session, collection, user)
    return collection


async def validate_collection_member_invite(
    collection: Collection = Depends(validate_collection_owner),
    session: AsyncSession = Depends(get_session),
    member_user: User = Depends(get_user),
    user: User = Depends(auth_required(forbid_thirdparty=True)),
) -> User:
    await check_hourly_rate_limit(
        session,
        user,
        constants.LOG_COLLECTION_MEMBER_INVITE,
        constants.COLLECTION_INVITES_RATE_LIMIT,
        inclusive=True,
    )

    if member_user.id == user.id:
        raise Abort("collections", "member-self")

    if member_user.banned:
        raise Abort("collections", "member-banned")

    # Any status counts here, re-inviting someone already pending is a
    # no-op at best and a notification spam vector at worst
    if await get_collection_member(
        session, collection.id, member_user, status=None
    ):
        raise Abort("collections", "member-exists")

    if (
        await service.count_collection_members(session, collection)
        >= constants.COLLECTION_MEMBERS_LIMIT
    ):
        raise Abort("collections", "member-limit")

    if (
        await service.count_user_pending_invites(session, member_user)
        >= constants.COLLECTION_INVITES_LIMIT
    ):
        raise Abort("collections", "member-invite-limit")

    # A decline is an explicit no, so it holds for a while. Without this
    # the owner could re-invite immediately, since declining hard deletes
    # the row and leaves nothing for the member-exists check to catch.
    # The log is the only record of a decline, and the decliner is always
    # its acting user
    if await count_logs(
        session,
        constants.LOG_COLLECTION_MEMBER_DECLINE,
        member_user,
        target_id=collection.id,
        start_time=utcnow()
        - timedelta(days=constants.COLLECTION_INVITE_COOLDOWN_DAYS),
    ):
        raise Abort("collections", "member-declined")

    return member_user


async def validate_collection_invite_accept(
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required(forbid_thirdparty=True)),
) -> CollectionMember:
    member = await get_collection_member_or_abort(session, collection, user)

    if member.status != constants.COLLECTION_MEMBER_PENDING:
        raise Abort("collections", "member-not-pending")

    return member


async def validate_collection_member_delete(
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
    member_user: User = Depends(get_member_user),
    user: User = Depends(auth_required(forbid_thirdparty=True)),
) -> CollectionMember:
    # Removing yourself is leaving the collection, or declining an invite,
    # and needs no ownership. Removing anybody else is owner only, and
    # since there is one owner, it can only be the owner leaving below
    if member_user.id != user.id:
        await require_collection_owner(session, collection, user)

    member = await get_collection_member_or_abort(
        session, collection, member_user
    )

    # The collection must always keep an owner
    if member.role == constants.COLLECTION_MEMBER_OWNER:
        raise Abort("collections", "owner-leave")

    return member


async def validate_collection_owner_offer(
    collection: Collection = Depends(validate_collection_owner),
    session: AsyncSession = Depends(get_session),
    member_user: User = Depends(get_user),
    user: User = Depends(auth_required(forbid_thirdparty=True)),
) -> CollectionMember:
    if member_user.id == user.id:
        raise Abort("collections", "already-owner")

    member = await get_collection_member_or_abort(
        session, collection, member_user
    )

    if member.status != constants.COLLECTION_MEMBER_ACCEPTED:
        raise Abort("collections", "member-not-accepted")

    if await service.get_collection_owner_offer(session, collection):
        raise Abort("collections", "owner-offer-exists")

    return member


async def validate_collection_owner_accept(
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required(forbid_thirdparty=True)),
) -> CollectionMember:
    offer = await service.get_collection_owner_offer(session, collection)

    # Only the person the collection was offered to may take it
    if not offer or offer.user_id != user.id:
        raise Abort("collections", "owner-offer-not-found")

    return offer


async def validate_collection_owner_cancel(
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required(forbid_thirdparty=True)),
) -> CollectionMember:
    offer = await service.get_collection_owner_offer(session, collection)

    if not offer:
        raise Abort("collections", "owner-offer-not-found")

    # Declined by the person it was offered to, or withdrawn by the owner.
    # Which of the two it was is recorded in the log's acting user
    if offer.user_id != user.id:
        await require_collection_owner(session, collection, user)

    return offer


async def validate_collection_members_list(
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(auth_required(optional=True)),
) -> bool:
    """Returns whether request user owns the collection"""

    return await is_collection_owner(session, collection.id, request_user)
