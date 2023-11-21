from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UsernameArgs, EmailArgs
from app.service import get_user_by_username
from app.dependencies import auth_required
from datetime import datetime, timedelta
from app.database import get_session
from app.errors import Abort
from app.models import User
from fastapi import Depends


async def validate_set_username(
    args: UsernameArgs,
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
) -> UsernameArgs:
    if user.last_username_change:
        if user.last_username_change + timedelta(hours=1) > datetime.utcnow():
            raise Abort("settings", "username-cooldown")

    if await get_user_by_username(session, args.username):
        raise Abort("settings", "username-taken")

    return args


async def validate_set_email(
    args: EmailArgs,
    session: AsyncSession = Depends(get_session),
) -> UsernameArgs:
    if await get_user_by_email(session, args.email):
        raise Abort("auth", "email-exists")

    return args
