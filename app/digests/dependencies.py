from app.dependencies import auth_required, get_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Digest, User
from app.errors import Abort
from fastapi import Depends
from app import constants
from . import service


async def validate_digest(
    name: str,
    user: User = Depends(get_user),
    session: AsyncSession = Depends(get_session),
):
    if not (digest := await service.get_digest(session, name, user)):
        raise Abort("digests", "not-found")

    return digest


async def validate_digest_info(
    digest: Digest = Depends(validate_digest),
    request_user: User | None = Depends(auth_required(optional=True)),
):
    if digest.private and digest.user != request_user:
        raise Abort("digests", "not-found")

    return digest


async def validate_digest_owner(
    name: str,
    request_user: User = Depends(auth_required(scope=[constants.SCOPE_UPLOAD])),
    session: AsyncSession = Depends(get_session),
):
    if not (digest := await service.get_digest(session, name, request_user)):
        raise Abort("digests", "not-found")

    return digest
