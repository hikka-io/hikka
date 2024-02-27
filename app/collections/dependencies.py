from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import check_user_permissions
from app.dependencies import auth_required
from app.models import Collection, User
from app.database import get_session
from .utils import check_consecutive
from .schemas import CollectionArgs
from app.errors import Abort
from fastapi import Depends
from app import constants
from uuid import UUID
from . import service


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

        if content.label and content.label not in labels:
            labels.append(content.label)
        else:
            unlabled_content = True

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
    collections_count = await service.get_user_collections_count(session, user)

    if collections_count >= 10:
        raise Abort("collections", "limit")

    return args


async def validate_collection(
    reference: UUID, session: AsyncSession = Depends(get_session)
) -> Collection:
    if not (collection := await service.get_collection(session, reference)):
        raise Abort("collections", "not-found")

    return collection


async def validate_collection_update(
    args: CollectionArgs = Depends(validate_collection_args),
    collection: Collection = Depends(validate_collection),
    user: User = Depends(auth_required()),
):
    if collection.content_type != args.content_type:
        raise Abort("collections", "bad-content-type")

    if user != collection.author and not check_user_permissions(
        user, [constants.PERMISSION_COLLECTION_UPDATE_MODERATOR]
    ):
        raise Abort("permission", "denied")

    # ToDo: log based rate limit

    return args


async def validate_collection_delete(
    collection: Collection = Depends(validate_collection),
    user: User = Depends(auth_required()),
):
    if collection.author != user:
        raise Abort("collections", "not-author")

    if user != collection.author and not check_user_permissions(
        user, [constants.PERMISSION_COLLECTION_DELETE_MODERATOR]
    ):
        raise Abort("permission", "denied")

    return collection
