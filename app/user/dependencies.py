from app.dependencies import auth_required, get_user, get_user_by_reference
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import User
from fastapi import Depends
from app import constants
from . import service


async def get_user_followed_reference(
    user: User = Depends(get_user_by_reference),
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_FOLLOW])
    ),
):
    return await service.load_is_followed(session, user, request_user)


async def get_user_followed_username(
    user: User = Depends(get_user),
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_FOLLOW])
    ),
):
    return await service.load_is_followed(session, user, request_user)
