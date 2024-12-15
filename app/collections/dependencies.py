from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.models import Collection, User
from app.database import get_session
from .utils import check_consecutive
from app.errors import Abort
from fastapi import Depends
from app import constants
from uuid import UUID
from . import service

from app.utils import (
    check_user_permissions,
    round_datetime,
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
    unlabled_content = False
    labels = []
    orders = []
    slugs = []

    for content in args.content:
        orders.append(content.order)
        slugs.append(content.slug)

        if not content.label:
            unlabled_content = True

        else:
            if content.label not in labels:
                labels.append(content.label)

    if len(labels) > 0 and unlabled_content:
        raise Abort("collections", "unlabled-content")

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


async def validate_collection_update(
    args: CollectionArgs = Depends(validate_collection_args),
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required()),
):
    if collection.content_type != args.content_type:
        raise Abort("collections", "bad-content-type")

    if user != collection.author:
        if not check_user_permissions(
            user, [constants.PERMISSION_COLLECTION_UPDATE_MODERATOR]
        ):
            raise Abort("permission", "denied")

        if collection.labels_order != args.labels_order:
            raise Abort("collections", "moderator-content-update")

        if not await service.content_compare(session, collection, args):
            raise Abort("collections", "moderator-content-update")

    # 1000 collection updates per hour should be sensible limit
    updates_limit = 1000
    logs_count = await count_logs(
        session,
        constants.LOG_COLLECTION_UPDATE,
        user,
        start_time=round_datetime(utcnow(), hours=1),
    )

    if (
        user.role
        not in [
            constants.ROLE_ADMIN,
            constants.ROLE_MODERATOR,
        ]
        and logs_count > updates_limit
    ):
        raise Abort("system", "rate-limit")

    return args


async def validate_collection_delete(
    collection: Collection = Depends(validate_collection),
    user: User = Depends(auth_required()),
):
    if collection.author != user and not check_user_permissions(
        user, [constants.PERMISSION_COLLECTION_DELETE_MODERATOR]
    ):
        raise Abort("permission", "denied")

    return collection
