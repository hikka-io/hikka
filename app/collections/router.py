from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import SuccessResponse
from app.models import Collection, User
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from . import service

from .schemas import (
    CollectionsListResponse,
    CollectionsListArgs,
    CollectionResponse,
    CollectionArgs,
)

from .dependencies import (
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
    request_user: User | None = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_COLLECTIONS])
    ),
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
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


@router.get("/{reference}", response_model=CollectionResponse)
async def get_collection(
    request_user: User | None = Depends(
        auth_required(
            optional=True,
            scope=[
                constants.SCOPE_READ_WATCHLIST,
                constants.SCOPE_READ_READLIST,
            ],
        )
    ),
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
):
    return await service.get_collection_display(
        session, collection, request_user
    )
