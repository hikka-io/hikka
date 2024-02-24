from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Collection, User
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from . import service

from .schemas import (
    CollectionsListResponse,
    CollectionInfoResponse,
    CollectionArgs,
)

from .dependencies import (
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

# ToDo: collection delete
# ToDo: logs for collection actions (create/update/delete)
# ToDo: collection content preview
# ToDo: tests
router = APIRouter(prefix="/collections", tags=["Collections"])


@router.get("", response_model=CollectionsListResponse)
async def get_collections(
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_collections_count(session)
    collections = await service.get_collections(session, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": collections.all(),
    }


@router.get("/user/{username}", response_model=CollectionsListResponse)
async def get_user_collections(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_user_collections_count(session, user)
    collections = await service.get_user_collections(
        session, user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": collections.all(),
    }


@router.post("/create", response_model=CollectionInfoResponse)
async def create_collection(
    session: AsyncSession = Depends(get_session),
    args: CollectionArgs = Depends(validate_collection_create),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_COLLECTION_CREATE])
    ),
):
    collection = await service.create_collection(session, args, user)
    return await service.get_collection_display(session, collection, user)


@router.put("/{reference}", response_model=CollectionInfoResponse)
async def update_collection(
    args: CollectionArgs = Depends(validate_collection_update),
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_COLLECTION_UPDATE])
    ),
):
    collection = await service.update_collection(session, collection, args)
    return await service.get_collection_display(session, collection, user)


@router.get("/{reference}", response_model=CollectionInfoResponse)
async def get_collection(
    request_user: User | None = Depends(auth_required(optional=True)),
    collection: Collection = Depends(validate_collection),
    session: AsyncSession = Depends(get_session),
):
    return await service.get_collection_display(
        session, collection, request_user
    )
