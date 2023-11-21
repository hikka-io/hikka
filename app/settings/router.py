from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from fastapi import APIRouter, Depends
from app.database import get_session
from app.schemas import PasswordArgs
from .schemas import DescriptionArgs
from app.models import User
from app import constants
from . import service

from app.service import (
    create_activation_token,
    create_email,
)

from .dependencies import (
    validate_set_username,
    validate_set_email,
)

from app.schemas import (
    UserResponse,
    UsernameArgs,
    EmailArgs,
)


router = APIRouter(prefix="/settings", tags=["Settings"])


@router.put(
    "/description",
    response_model=UserResponse,
    summary="Change description",
)
async def change_description(
    args: DescriptionArgs,
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
):
    return await service.change_description(session, user, args.description)


@router.put(
    "/password",
    response_model=UserResponse,
    summary="Change password",
)
async def change_password(
    args: PasswordArgs,
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
):
    return await service.set_password(session, user, args.password)


@router.put(
    "/username",
    response_model=UserResponse,
    summary="Change username",
)
async def change_username(
    args: UsernameArgs = Depends(validate_set_username),
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
):
    return await service.set_username(session, user, args.username)


@router.put(
    "/email",
    response_model=UserResponse,
    summary="Set a email",
)
async def change_email(
    args: EmailArgs = Depends(validate_set_email),
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
):
    user = await service.set_email(session, user, args.email)
    user = await create_activation_token(session, user)

    # Add new activation email to database
    await create_email(
        session,
        constants.EMAIL_ACTIVATION,
        user.activation_token,
        user,
    )

    return user
