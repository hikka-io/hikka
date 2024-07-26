from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from app.dependencies import auth_required
from app.schemas import ClientResponse
from app.database import get_session
from app.models import Client, User
from app.client import service
from app import constants

from app.client.dependencies import (
    validate_client_create,
    user_client_required,
    validate_client,
)
from app.client.schemas import (
    ClientFullResponse,
    ClientCreate,
    ClientUpdate,
)

router = APIRouter(prefix="/client", tags=["Client"])


@router.get("/", summary="Get user client", response_model=ClientFullResponse)
async def get_user_client(client: Client = Depends(user_client_required)):
    return client


@router.get(
    "/{client_reference}",
    summary="Get client by reference",
    response_model=ClientResponse,
)
async def get_client_by_reference(client: Client = Depends(validate_client)):
    return client


@router.post(
    "/", summary="Create new user client", response_model=ClientFullResponse
)
async def create_user_client(
    create: ClientCreate = Depends(validate_client_create),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_CLIENT_CREATE])
    ),
):
    return await service.create_user_client(session, user, create)


@router.put(
    "/",
    summary="Update user client",
    response_model=ClientFullResponse,
    dependencies=[
        Depends(auth_required(permissions=[constants.PERMISSION_CLIENT_UPDATE]))
    ],
)
async def update_user_client(
    update: ClientUpdate,
    session: AsyncSession = Depends(get_session),
    client: Client = Depends(user_client_required),
):
    return await service.update_client(session, client, update)


@router.delete(
    "/",
    summary="Delete user client",
    response_model=ClientFullResponse,
    dependencies=[
        Depends(auth_required(permissions=[constants.PERMISSION_CLIENT_DELETE]))
    ],
)
async def delete_user_client(
    session: AsyncSession = Depends(get_session),
    client: Client = Depends(user_client_required),
):
    return await service.delete_client(session, client)
