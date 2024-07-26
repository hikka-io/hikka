from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import URL
from fastapi import Depends

from app.dependencies import auth_required
from app.database import get_session
from app.models import User, Client
from .schemas import ClientCreate
from app.errors import Abort
from . import service


async def user_client_required(
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
) -> Client:
    if (client := await service.get_user_client(session, user)) is None:
        raise Abort("client", "not-found")

    return client


async def validate_client_create(
    create: ClientCreate,
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
):
    if (await service.get_user_client(session, user)) is not None:
        raise Abort("client", "already-exists")

    if URL(create.endpoint):
        pass

    return create


async def validate_client(
    client_reference: str,
    session: AsyncSession = Depends(get_session),
) -> Client:
    if not (client := await service.get_client(session, client_reference)):
        raise Abort("client", "not-found")

    return client
