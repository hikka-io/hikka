from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from app.dependencies import auth_required, get_page, get_size
from app.utils import pagination, paginated_response
from app.schemas import ClientResponse
from app.database import get_session
from app.models import Client, User
from app.client import service
from app import constants

from app.client.dependencies import (
    validate_unverified_client,
    validate_client_create,
    validate_user_client,
    validate_client,
)
from app.client.schemas import (
    ClientPaginationResponse,
    ClientFullResponse,
    ListAllClientsArgs,
    ClientCreate,
    ClientUpdate,
)

router = APIRouter(prefix="/client", tags=["Client"])


@router.get(
    "", summary="List user clients", response_model=ClientPaginationResponse
)
async def list_user_clients(
    page: int = Depends(get_page),
    size: int = Depends(get_size),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_READ_CLIENT_LIST])
    ),
):
    limit, offset = pagination(page, size)

    total = await service.count_user_clients(session, user, offset, limit)
    clients = await service.list_user_clients(session, user, offset, limit)

    return paginated_response(clients.all(), total, page, limit)


@router.post(
    "/all",
    summary="List all clients",
    response_model=ClientPaginationResponse,
    dependencies=[
        Depends(
            auth_required(
                scope=[constants.SCOPE_READ_CLIENT_LIST],
                permissions=[constants.PERMISSION_CLIENT_LIST_ALL],
            )
        )
    ],
)
async def list_all_clients(
    args: ListAllClientsArgs,
    page: int = Depends(get_page),
    size: int = Depends(get_size),
    session: AsyncSession = Depends(get_session),
):
    limit, offset = pagination(page, size)

    total = await service.count_all_clients(session, args)
    clients = await service.list_all_clients(session, args, offset, limit)

    return paginated_response(clients.all(), total, page, limit)


@router.get(
    "/{client_reference}",
    summary="Get client by reference",
    response_model=ClientResponse,
)
async def get_client_by_reference(client: Client = Depends(validate_client)):
    return client


@router.get(
    "/{client_reference}/full",
    summary="Get user full client by reference",
    response_model=ClientFullResponse,
    dependencies=[Depends(auth_required(scope=[constants.SCOPE_READ_CLIENT]))],
)
async def get_user_client(client: Client = Depends(validate_user_client)):
    return client


@router.post(
    "", summary="Create new user client", response_model=ClientFullResponse
)
async def create_user_client(
    create: ClientCreate = Depends(validate_client_create),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_CLIENT_CREATE],
            scope=[constants.SCOPE_CREATE_CLIENT],
        )
    ),
):
    return await service.create_user_client(session, user, create)


@router.put(
    "/{client_reference}",
    summary="Update user client",
    response_model=ClientFullResponse,
    dependencies=[
        Depends(
            auth_required(
                permissions=[constants.PERMISSION_CLIENT_UPDATE],
                scope=[constants.SCOPE_UPDATE_CLIENT],
            )
        )
    ],
)
async def update_user_client(
    update: ClientUpdate,
    session: AsyncSession = Depends(get_session),
    client: Client = Depends(validate_user_client),
):
    return await service.update_client(session, client, update)


@router.delete(
    "/{client_reference}",
    summary="Delete user client",
    response_model=ClientFullResponse,
    dependencies=[
        Depends(
            auth_required(
                permissions=[constants.PERMISSION_CLIENT_DELETE],
                scope=[constants.SCOPE_DELETE_CLIENT],
            )
        )
    ],
)
async def delete_user_client(
    session: AsyncSession = Depends(get_session),
    client: Client = Depends(validate_user_client),
):
    return await service.delete_client(session, client)


@router.post(
    "/{client_reference}/verify",
    summary="Verify third-party client",
    response_model=ClientResponse,
    dependencies=[
        Depends(
            auth_required(
                permissions=[constants.PERMISSION_CLIENT_VERIFY],
                scope=[constants.SCOPE_VERIFY_CLIENT],
            )
        )
    ],
)
async def verify_third_party_client(
    session: AsyncSession = Depends(get_session),
    client: Client = Depends(validate_unverified_client),
):
    return await service.verify_client(session, client)
