from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.database import get_session
from app.models import User
from fastapi import Depends
from app import constants


async def verify_test(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_TEST])
    ),
) -> User:
    return user
