from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import SuccessResponse
from app.models import Collection, User
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from . import service

from .schemas import (
    CollectionsListResponse,
    CollectionResponse,
    CollectionArgs,
)

from .dependencies import (
    validate_collection_delete,
    validate_collection_update,
    validate_collection_create,
    validate_collection,
)

from app.utils import (
    pagination_dict,
    pagination,
)

from app.dependencies import (
    auth_required,
    get_user,
    get_page,
    get_size,
)

# ToDo: logs for collection actions (create/update/delete)
# ToDo: tests
router = APIRouter(prefix="/collections", tags=["Collections"])


@router.get("", response_model=CollectionsListResponse)
async def get_collections(
    request_user: User | None = Depends(auth_required(optional=True)),
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_collections_count(session)
    collections = await service.get_collections(
        session, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": collections.unique().all(),
    }


@router.get("/user/{username}", response_model=CollectionsListResponse)
async def get_user_collections(
    request_user: User | None = Depends(auth_required(optional=True)),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_user_collections_count(session, user)
    collections = await service.get_user_collections(
        session, user, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": collections.unique().all(),
    }


@router.post("/create", response_model=CollectionResponse)
async def create_collection(
    session: AsyncSession = Depends(get_session),
    args: CollectionArgs = Depends(validate_collection_create),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_COLLECTION_CREATE])
    ),
):
    collection = await service.create_collection(session, args, user)
    return await service.get_collection_display(session, collection, user)


@router.get("/{reference}", response_model=CollectionResponse)
async def get_collection(
    request_user: User | None = Depends(auth_required(optional=True)),
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
):
    return await service.get_collection_display(
        session, collection, request_user
    )


@router.put("/{reference}", response_model=CollectionResponse)
async def update_collection(
    args: CollectionArgs = Depends(validate_collection_update),
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_COLLECTION_UPDATE])
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
        auth_required(permissions=[constants.PERMISSION_COLLECTION_DELETE])
    ),
):
    await service.delete_collection(session, collection, user)
    return {"success": True}
