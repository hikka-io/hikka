from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.models import Comment, Edit, User
from datetime import datetime, timedelta
from app.database import get_session
from .schemas import CollectionArgs
from app.errors import Abort
from fastapi import Depends


async def validate_collection_args(
    args: CollectionArgs,
    session: AsyncSession = Depends(get_session),
):
    return args


async def validate_collection_create(
    args: CollectionArgs = Depends(validate_collection_args),
):
    return args
