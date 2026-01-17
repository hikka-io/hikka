from fastapi import APIRouter, BackgroundTasks, Depends
from app.common.schemas import UserCustomizationArgs
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.database import get_session
from app.models import User
from app import constants
from . import service

from app.schemas import (
    SuccessResponse,
    UserResponse,
    PasswordArgs,
    UsernameArgs,
    EmailArgs,
)

from app.service import (
    create_activation_token,
    create_email,
)

from .schemas import (
    IgnoredNotificationsResponse,
    IgnoredNotificationsArgs,
    ReadDeleteContenType,
    ImportWatchListArgs,
    ImportReadListArgs,
    UserExportResponse,
    DescriptionArgs,
    ImageTypeEnum,
)

from .dependencies import (
    validate_set_username,
    validate_set_email,
)


router = APIRouter(prefix="/settings", tags=["Settings"])


@router.put(
    "/description",
    response_model=UserResponse,
    summary="Change description",
)
async def change_description(
    args: DescriptionArgs,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_UPDATE_USER_DESCRIPTION])
    ),
):
    return await service.change_description(session, user, args.description)


@router.put(
    "/ui",
    response_model=SuccessResponse,
)
async def change_ui(
    args: UserCustomizationArgs,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_UPDATE_USER_CUSTOMIZATION])
    ),
):
    await service.set_customization(session, user, args)
    return {"success": True}


@router.put(
    "/password",
    response_model=UserResponse,
    summary="Change password",
)
async def change_password(
    args: PasswordArgs,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_UPDATE_USER_PASSWORD])
    ),
):
    return await service.set_password(session, user, args.password)


@router.put(
    "/username",
    response_model=UserResponse,
    summary="Change username",
)
async def change_username(
    session: AsyncSession = Depends(get_session),
    args: UsernameArgs = Depends(validate_set_username),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_UPDATE_USER_USERNAME])
    ),
):
    return await service.set_username(session, user, args.username)


@router.put(
    "/email",
    response_model=UserResponse,
    summary="Set a email",
)
async def change_email(
    session: AsyncSession = Depends(get_session),
    args: EmailArgs = Depends(validate_set_email),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_UPDATE_USER_EMAIL])
    ),
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


@router.post(
    "/import/watch",
    response_model=SuccessResponse,
    summary="Import watch list",
)
async def import_watch(
    args: ImportWatchListArgs,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_UPDATE_WATCHLIST])
    ),
):
    # Run watch list import in background
    # This task may block event loop so we should keep that in mind
    # https://stackoverflow.com/a/67601373
    background_tasks.add_task(
        service.import_watch_list,
        session,
        args,
        user,
    )

    return {"success": True}


@router.post(
    "/import/read",
    response_model=SuccessResponse,
    summary="Import read list",
)
async def import_read(
    args: ImportReadListArgs,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_UPDATE_READLIST])
    ),
):
    # Run watch list import in background
    # This task may block event loop so we should keep that in mind
    # https://stackoverflow.com/a/67601373
    background_tasks.add_task(
        service.import_read_list,
        session,
        args,
        user,
    )

    return {"success": True}


@router.post(
    "/export",
    response_model=UserExportResponse,
    summary="Export list",
)
async def export_list(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required(scope=[constants.SCOPE_EXPORT_LIST])),
):
    return await service.get_export_list(session, user)


@router.put(
    "/notifications",
    response_model=IgnoredNotificationsResponse,
    summary="Change ignored notification types",
)
async def change_ignored_notifications(
    args: IgnoredNotificationsArgs,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_UPDATE_USER_DETAILS])
    ),
):
    return await service.set_ignored_notifications(
        session, user, args.ignored_notifications
    )


@router.get(
    "/notifications",
    response_model=IgnoredNotificationsResponse,
    summary="Get ignored notification types",
)
async def get_ignored_notifications(
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_READ_USER_DETAILS])
    ),
):
    return user


@router.delete(
    "/image/{image_type}",
    response_model=UserResponse,
    summary="Delete user image",
)
async def delete_user_image(
    image_type: ImageTypeEnum,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            scope=[
                constants.SCOPE_DELETE_USER_IMAGE,
                constants.SCOPE_DELETE_USER_COVER,
            ]
        )
    ),
):
    return await service.delete_user_image(session, user, image_type)


@router.delete(
    "/watch",
    response_model=SuccessResponse,
    summary="Delete user watch list",
)
async def delete_user_watch(
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_UPDATE_WATCHLIST])
    ),
):
    # Run watch list import in background
    # This task may block event loop so we should keep that in mind
    # https://stackoverflow.com/a/67601373
    background_tasks.add_task(
        service.delete_user_watch,
        session,
        user,
    )

    return {"success": True}


@router.delete(
    "/read/{content_type}",
    response_model=SuccessResponse,
    summary="Delete user watch list",
)
async def delete_user_read(
    content_type: ReadDeleteContenType,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_UPDATE_WATCHLIST])
    ),
):
    # Run watch list import in background
    # This task may block event loop so we should keep that in mind
    # https://stackoverflow.com/a/67601373
    background_tasks.add_task(
        service.delete_user_read,
        session,
        user,
        content_type,
    )

    return {"success": True}
