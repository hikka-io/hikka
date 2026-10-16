import secrets
import uuid

from sqlalchemy import select, update, func, ScalarResult, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.client.schemas import ClientCreate, ClientUpdate, ListAllClientsArgs
from app.models import AuthTokenRequest, AuthToken, User, Client
from app.utils import utcnow


def _client_secret():
    return secrets.token_urlsafe(96)


async def get_client(
    session: AsyncSession, reference: str | uuid.UUID
) -> Client:
    return await session.scalar(
        select(Client)
        .filter(
            Client.id == reference,
            Client.deleted == False,  # noqa: E712
        )
        .options(joinedload(Client.user))
    )


async def get_user_client(
    session: AsyncSession, user: User, name: str
) -> Client:
    return await session.scalar(
        select(Client).filter(
            Client.user_id == user.id,
            func.lower(Client.name) == name.lower(),
            Client.deleted == False,  # noqa: E712
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
            Client.deleted == False,  # noqa: E712
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
        .filter(
            Client.user_id == user.id,
            Client.deleted == False,  # noqa: E712
        )
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
    now = utcnow()

    client.deleted = True
    client.updated = now

    # Once client is deleted we should expire related tokens and requests
    await session.execute(
        update(AuthToken)
        .filter(AuthToken.client_id == client.id, AuthToken.expiration > now)
        .values(expiration=now)
    )

    await session.execute(
        update(AuthTokenRequest)
        .filter(
            AuthTokenRequest.client_id == client.id,
            AuthTokenRequest.expiration > now,
        )
        .values(expiration=now)
    )

    await session.commit()
    return client


async def verify_client(session: AsyncSession, client: Client) -> Client:
    client.verified = True
    await session.commit()
    return client


def apply_all_clients_filters(
    query: Select, args: ListAllClientsArgs
) -> Select:
    query = query.filter(Client.deleted == False)  # noqa: E712

    if args.query is not None:
        query = query.filter(Client.name.ilike(f"%{args.query}%"))

    return query


async def count_all_clients(
    session: AsyncSession, args: ListAllClientsArgs
) -> int:
    return await session.scalar(
        apply_all_clients_filters(select(func.count(Client.id)), args)
    )


async def list_all_clients(
    session: AsyncSession, args: ListAllClientsArgs, offset: int, limit: int
) -> ScalarResult[Client]:
    return await session.scalars(
        apply_all_clients_filters(
            select(Client)
            .options(joinedload(Client.user))
            .order_by(Client.created.desc())
            .offset(offset)
            .limit(limit),
            args,
        )
    )
