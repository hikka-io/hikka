from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User
from . import service


from .schemas import (
    ModerationPaginationResponse,
    ModerationSearchArgs,
)

from .dependencies import validate_moderation_search_args

from app.utils import (
    pagination_dict,
    pagination,
)

from app.dependencies import (
    get_page,
    get_size,
    get_user,
)


router = APIRouter(prefix="/moderation", tags=["Moderation"])


@router.post(
    "/log",
    response_model=ModerationPaginationResponse,
    summary="Moderation log",
)
async def moderation_log(
    args: ModerationSearchArgs = Depends(validate_moderation_search_args),
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_moderation_count(session, args)
    moderation = await service.get_moderation(session, args, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": moderation.all(),
    }


@router.get(
    "/{username}/log",
    response_model=ModerationPaginationResponse,
    summary="User moderation log",
)
async def moderation_user_log(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_user_moderation_count(session, user.id)
    moderation = await service.get_user_moderation(
        session, user.id, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": moderation.all(),
    }
