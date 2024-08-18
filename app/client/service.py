import secrets
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func, ScalarResult

from app.client.schemas import ClientCreate, ClientUpdate
from app.models import User, Client
from app.utils import utcnow


def _client_secret():
    return secrets.token_urlsafe(96)


async def get_client(
    session: AsyncSession, reference: str | uuid.UUID
) -> Client:
    return await session.scalar(
        select(Client)
        .filter(Client.id == reference)
        .options(joinedload(Client.user))
    )


async def get_user_client(
    session: AsyncSession, user: User, name: str
) -> Client:
    return await session.scalar(
        select(Client).filter(
            Client.user_id == user.id, func.lower(Client.name) == name.lower()
        )
    )


async def list_user_clients(
    session: AsyncSession,
    user: User,
    offset: int,
    limit: int,
) -> ScalarResult[Client]:
    return await session.scalars(
        select(Client)
        .filter(
            Client.user_id == user.id,
        )
        .offset(offset)
        .limit(limit)
        .order_by(Client.created.asc())
    )


async def count_user_clients(
    session: AsyncSession,
    user: User,
    offset: int,
    limit: int,
) -> int:
    return await session.scalar(
        select(func.count(Client.id))
        .filter(Client.user_id == user.id)
        .offset(offset)
        .limit(limit)
    )


async def create_user_client(
    session: AsyncSession, user: User, create: ClientCreate
) -> Client:
    now = utcnow()

    client = Client(
        **{
            "secret": _client_secret(),
            "name": create.name,
            "description": create.description,
            "endpoint": str(create.endpoint),
            "user_id": user.id,
            "created": now,
            "updated": utcnow(),
        }
    )

    session.add(client)
    await session.commit()

    return client


async def update_client(
    session: AsyncSession, client: Client, update: ClientUpdate
) -> Client:
    now = utcnow()

    if update.name is not None:
        client.name = update.name

    if update.description is not None:
        client.description = update.description

    if update.endpoint is not None:
        client.endpoint = str(update.endpoint)

    if update.revoke_secret:
        client.secret = _client_secret()

    client.updated = now

    await session.commit()

    return client


async def delete_client(session: AsyncSession, client: Client) -> Client:
    await session.delete(client)
    await session.commit()
    return client


async def verify_client(session: AsyncSession, client: Client) -> Client:
    client.verified = True
    await session.commit()
    return client
