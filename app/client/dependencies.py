import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.dependencies import auth_required
from app.database import get_session
from app.models import User, Client
from .schemas import ClientCreate
from app.errors import Abort
from app import constants
from . import service


async def validate_client_create(
    create: ClientCreate,
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
):
    if (await service.get_user_client(session, user, create.name)) is not None:
        raise Abort("client", "already-exists")

    if (
        await service.count_user_clients(
            session, user, 0, constants.MAX_USER_CLIENTS
        )
    ) == constants.MAX_USER_CLIENTS:
        raise Abort("client", "max-clients")

    return create


async def validate_client(
    client_reference: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> Client:
    if not (client := await service.get_client(session, client_reference)):
        raise Abort("client", "not-found")

    return client


async def validate_user_client(
    client: Client = Depends(validate_client),
    user: User = Depends(auth_required()),
):
    if client.user_id != user.id:
        raise Abort("client", "not-owner")

    return client
