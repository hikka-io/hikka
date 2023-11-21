from sqlalchemy.ext.asyncio import AsyncSession
from app.service import get_user_by_username
from app.database import get_session
from app.schemas import UsernameArgs
from app.errors import Abort
from fastapi import Depends


async def validate_set_username(
    args: UsernameArgs,
    session: AsyncSession = Depends(get_session),
) -> UsernameArgs:
    if await get_user_by_username(session, args.username):
        raise Abort("settings", "username-taken")

    return args
