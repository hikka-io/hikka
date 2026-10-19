from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import SuccessResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from . import service

from app.models import (
    CollectionContent,
    Collection,
    Character,
    Person,
    Anime,
    Manga,
    Novel,
    User,
)

from .schemas import (
    UserCollectionsListResponse,
    CollectionContentAddArgs,
    CollectionsListResponse,
    UserCollectionResponse,
    CollectionsListArgs,
    CollectionResponse,
    UserCollectionsArgs,
    CollectionArgs,
)

from .dependencies import (
    validate_collection_content_delete,
    validate_collection_content_update,
    validate_collection_content_add,
    validate_collections_list_args,
    validate_user_collections_args,
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


@router.get("/me", response_model=UserCollectionsListResponse)
async def get_user_collections(
    args: UserCollectionsArgs = Depends(validate_user_collections_args),
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_READ_COLLECTIONS])
    ),
):
    limit, offset = pagination(page, size)
    total = await service.get_user_collections_count(session, user, args)
    collections = await service.get_user_collections(
        session, user, args, limit, offset
    )

    return paginated_response(collections.all(), total, page, limit)


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


@router.put(
    "/{reference}/content/{slug}", response_model=UserCollectionResponse
)
async def add_collection_content(
    slug: str,
    args: CollectionContentAddArgs,
    content: Anime | Manga | Novel | Character | Person = Depends(
        validate_collection_content_add
    ),
    collection: Collection = Depends(validate_collection_content_update),
    session: AsyncSession = Depends(get_session),
):
    collection = await service.add_collection_content(
        session, collection, content, args, collection.author
    )

    return await service.get_user_collection_display(session, collection, slug)


@router.delete(
    "/{reference}/content/{slug}", response_model=UserCollectionResponse
)
async def delete_collection_content(
    slug: str,
    entry: CollectionContent = Depends(validate_collection_content_delete),
    collection: Collection = Depends(validate_collection_content_update),
    session: AsyncSession = Depends(get_session),
):
    collection = await service.delete_collection_content(
        session, collection, entry, collection.author
    )

    return await service.get_user_collection_display(session, collection, slug)
