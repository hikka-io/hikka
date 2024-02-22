from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Notification, User
from fastapi import APIRouter, Depends
from app.database import get_session
from .schemas import CollectionArgs
from . import service

from .dependencies import (
    validate_collection_create,
)

from app.utils import (
    pagination_dict,
    pagination,
)

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)


router = APIRouter(prefix="/collections", tags=["Collections"])


@router.post(
    "/create",
    # response_model=WatchResponse,
)
async def create_collection(
    session: AsyncSession = Depends(get_session),
    args: CollectionArgs = Depends(validate_collection_create),
):
    return args
