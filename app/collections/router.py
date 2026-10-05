from app.models import CollectionMember, Collection, User
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import SuccessResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from . import service

from .schemas import (
    CollectionMembersResponse,
    CollectionMemberResponse,
    CollectionsListResponse,
    CollectionsListArgs,
    CollectionResponse,
    CollectionArgs,
)

from .dependencies import (
    validate_collection_owner_accept,
    validate_collection_owner_cancel,
    validate_collection_owner_offer,
    validate_collection_member_invite,
    validate_collection_member_delete,
    validate_collection_invite_accept,
    validate_collection_members_list,
    validate_collections_list_args,
    validate_collection_delete,
    validate_collection_update,
    validate_collection_create,
    validate_collection,
)

from app.utils import (
    paginated_response,
    pagination,
)

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)


router = APIRouter(prefix="/collections", tags=["Collections"])


@router.post("", response_model=CollectionsListResponse)
async def get_collections(
    args: CollectionsListArgs = Depends(validate_collections_list_args),
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
    request_user: User | None = Depends(
        auth_required(
            scope=[constants.SCOPE_READ_COLLECTIONS],
            optional=True,
        )
    ),
):
    limit, offset = pagination(page, size)
    total = await service.get_collections_count(session, request_user, args)
    collections = await service.get_collections(
        session, request_user, args, limit, offset
    )

    return paginated_response(collections.unique().all(), total, page, limit)


@router.post("/create", response_model=CollectionResponse)
async def create_collection(
    session: AsyncSession = Depends(get_session),
    args: CollectionArgs = Depends(validate_collection_create),
    user: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_COLLECTION_CREATE],
            scope=[constants.SCOPE_CREATE_COLLECTION],
        )
    ),
):
    collection = await service.create_collection(session, args, user)
    return await service.get_collection_display(session, collection, user)


@router.put("/{reference}", response_model=CollectionResponse)
async def update_collection(
    args: CollectionArgs = Depends(validate_collection_update),
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_COLLECTION_UPDATE],
            scope=[constants.SCOPE_UPDATE_COLLECTION],
        )
    ),
):
    collection = await service.update_collection(
        session, collection, args, user
    )

    return await service.get_collection_display(session, collection, user)


@router.delete("/{reference}", response_model=SuccessResponse)
async def delete_collection(
    collection: Collection = Depends(validate_collection_delete),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_COLLECTION_DELETE],
            scope=[constants.SCOPE_DELETE_COLLECTION],
        )
    ),
):
    await service.delete_collection(session, collection, user)
    return {"success": True}


@router.get("/{reference}/members", response_model=CollectionMembersResponse)
async def get_collection_members(
    collection: Collection = Depends(validate_collection),
    is_owner: bool = Depends(validate_collection_members_list),
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(
        auth_required(
            optional=True, scope=[constants.SCOPE_READ_COLLECTIONS]
        )
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_collection_members_count(
        session, collection, request_user, is_owner
    )
    members = await service.get_collection_members(
        session, collection, request_user, is_owner, limit, offset
    )

    return paginated_response(members.all(), total, page, limit)


@router.post(
    "/{reference}/members/accept", response_model=CollectionMemberResponse
)
async def accept_collection_invite(
    collection: Collection = Depends(validate_collection),
    member: CollectionMember = Depends(validate_collection_invite_accept),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_COLLECTION_UPDATE],
            forbid_thirdparty=True,
        )
    ),
):
    return await service.accept_collection_invite(
        session, collection, member, user
    )


@router.put(
    "/{reference}/members/{username}",
    response_model=CollectionMemberResponse,
)
async def invite_collection_member(
    collection: Collection = Depends(validate_collection),
    member_user: User = Depends(validate_collection_member_invite),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_COLLECTION_UPDATE],
            forbid_thirdparty=True,
        )
    ),
):
    return await service.invite_collection_member(
        session, collection, member_user, user
    )


@router.delete(
    "/{reference}/members/{username}", response_model=SuccessResponse
)
async def delete_collection_member(
    collection: Collection = Depends(validate_collection),
    member: CollectionMember = Depends(validate_collection_member_delete),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_COLLECTION_UPDATE],
            forbid_thirdparty=True,
        )
    ),
):
    await service.delete_collection_member(session, collection, member, user)
    return {"success": True}


@router.post("/{reference}/owner/accept", response_model=SuccessResponse)
async def accept_collection_ownership(
    collection: Collection = Depends(validate_collection),
    offer: CollectionMember = Depends(validate_collection_owner_accept),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_COLLECTION_UPDATE],
            forbid_thirdparty=True,
        )
    ),
):
    await service.accept_collection_ownership(
        session, collection, offer, user
    )
    return {"success": True}


@router.put(
    "/{reference}/owner/{username}",
    response_model=CollectionMemberResponse,
)
async def offer_collection_ownership(
    collection: Collection = Depends(validate_collection),
    member: CollectionMember = Depends(validate_collection_owner_offer),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_COLLECTION_UPDATE],
            forbid_thirdparty=True,
        )
    ),
):
    return await service.offer_collection_ownership(
        session, collection, member, user
    )


@router.delete("/{reference}/owner", response_model=SuccessResponse)
async def cancel_collection_ownership_offer(
    collection: Collection = Depends(validate_collection),
    offer: CollectionMember = Depends(validate_collection_owner_cancel),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_COLLECTION_UPDATE],
            forbid_thirdparty=True,
        )
    ),
):
    await service.cancel_collection_ownership_offer(
        session, collection, offer, user
    )
    return {"success": True}


@router.get("/{reference}", response_model=CollectionResponse)
async def get_collection(
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(
        auth_required(
            optional=True,
            scope=[
                constants.SCOPE_READ_WATCHLIST,
                constants.SCOPE_READ_READLIST,
            ],
        )
    ),
):
    return await service.get_collection_display(
        session, collection, request_user
    )
