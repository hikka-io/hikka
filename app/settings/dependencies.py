from app.utils import is_protected_username, utcnow
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UsernameArgs, EmailArgs
from app.dependencies import auth_required
from app.database import get_session
from datetime import timedelta
from app.errors import Abort
from app.models import User
from fastapi import Depends

from app.service import (
    get_user_by_username,
    get_user_by_email,
)


async def validate_set_username(
    args: UsernameArgs,
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
) -> UsernameArgs:
    if user.last_username_change:
        if user.last_username_change + timedelta(hours=1) > utcnow():
            raise Abort("settings", "username-cooldown")

    if is_protected_username(args.username):
        raise Abort("settings", "invalid-username")

    if username_owner := await get_user_by_username(session, args.username):
        # If the username belongs to the user doing the request then it's fine
        if username_owner.id != user.id:
            raise Abort("settings", "username-taken")

    return args


async def validate_set_email(
    args: EmailArgs,
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
) -> UsernameArgs:
    if user.last_email_change:
        if user.last_email_change + timedelta(days=1) > utcnow():
            raise Abort("settings", "email-cooldown")

    if await get_user_by_email(session, args.email):
        raise Abort("auth", "email-exists")

    return args
