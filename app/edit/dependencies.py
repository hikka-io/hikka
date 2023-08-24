from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.database import get_session
from app.models import User
from fastapi import Depends


async def verify_test(
    user: User = Depends(auth_required(permissions=["system:test"])),
    session: AsyncSession = Depends(get_session),
) -> User:
    return user
