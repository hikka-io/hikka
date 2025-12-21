from app.dependencies import auth_required, get_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.errors import Abort
from app.models import User
from fastapi import Depends
from app import constants
from . import service


async def validate_artifact(
    name: str,
    user: User = Depends(get_user),
    request_user: User | None = Depends(auth_required(optional=True)),
    session: AsyncSession = Depends(get_session),
):
    if not (artifact := await service.get_artifact(session, name, user)):
        raise Abort("artifacts", "not-found")

    if artifact.private and artifact.user != request_user:
        raise Abort("artifacts", "not-found")

    return artifact


async def validate_artifact_owner(
    name: str,
    request_user: User = Depends(auth_required(scope=[constants.SCOPE_UPLOAD])),
    session: AsyncSession = Depends(get_session),
):
    if not (
        artifact := await service.get_artifact(session, name, request_user)
    ):
        raise Abort("artifacts", "not-found")

    return artifact
