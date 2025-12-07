from typing import Literal
from app.dependencies import auth_required, get_user, get_user_by_reference
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import User
from fastapi import Depends
from app import constants
from . import service


def get_user_followed(by: Literal["reference", "username"]):
    match by:
        case "reference":
            user_dependency = get_user_by_reference
        case "username":
            user_dependency = get_user

    async def dependency(
        user: User = Depends(user_dependency),
        session: AsyncSession = Depends(get_session),
        request_user: User | None = Depends(
            auth_required(optional=True, scope=[constants.SCOPE_READ_FOLLOW])
        ),
    ):
        return await service.load_is_followed(session, user, request_user)

    return dependency
