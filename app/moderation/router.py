from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app import constants
from app.database import get_session
from app.models import User
from . import service


from .schemas import (
    ModerationPaginationResponse,
)

from app.utils import (
    pagination_dict,
    pagination,
)

from app.dependencies import (
    get_page,
    get_size,
    get_user,
)


class ModerationError(Exception):
    def __init__(self, content: dict, status_code: int):
        self.status_code = status_code
        self.content = content


router = APIRouter(prefix="/moderation", tags=["Moderation"])


@router.get(
    "/log",
    response_model=ModerationPaginationResponse,
    summary="Moderation log",
)
async def moderation_log(
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_moderation_count(session)
    moderation = await service.get_moderation(session, limit, offset)

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
