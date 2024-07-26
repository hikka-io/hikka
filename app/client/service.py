import secrets
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.client.schemas import ClientCreate, ClientUpdate
from app.models import User, Client
from app.utils import utcnow


def _client_secret():
    return secrets.token_urlsafe(96)


async def get_client(session: AsyncSession, reference: str | uuid.UUID) -> Client:
    return await session.scalar(select(Client).filter(Client.id == reference))


async def get_user_client(session: AsyncSession, user: User) -> Client:
    return await session.scalar(
        select(Client).filter(Client.user_id == user.id)
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
        }
    )

    session.add(client)
    await session.commit()

    return client


async def update_client(
    session: AsyncSession, client: Client, update: ClientUpdate
) -> Client:
    if update.name is not None:
        client.name = update.name

    if update.description is not None:
        client.description = update.description

    if update.endpoint is not None:
        client.endpoint = str(update.endpoint)

    if update.revoke_secret is not None:
        client.secret = _client_secret()

    await session.commit()

    return client


async def delete_client(session: AsyncSession, client: Client) -> Client:
    await session.delete(client)
    await session.commit()
    return client
