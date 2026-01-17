from app.dependencies import auth_required, get_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import User
from fastapi import Depends
from app import constants
from . import service


async def get_user_followed(
    user: User = Depends(get_user),
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_FOLLOW])
    ),
):
    return await service.load_is_followed(session, user, request_user)
