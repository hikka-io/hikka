from sqlalchemy.ext.asyncio import AsyncSession
from app.service import get_user_by_username
from app.database import get_session
from app.errors import Abort
from app.models import User
from fastapi import Depends


async def get_profile(
    username: str,
    session: AsyncSession = Depends(get_session),
) -> User:
    if not (user := await get_user_by_username(session, username)):
        raise Abort("user", "not-found")

    return user
