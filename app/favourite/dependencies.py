from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import FavouriteContentTypeEnum
from app.models import Anime, User, Favourite
from app.service import get_content_by_slug
from app.dependencies import auth_required
from app.database import get_session
from app.errors import Abort
from fastapi import Depends
from . import service


async def validate_content(
    slug: str,
    content_type: FavouriteContentTypeEnum,
    session: AsyncSession = Depends(get_session),
) -> Anime:
    if not (content := await get_content_by_slug(session, content_type, slug)):
        raise Abort("favourite", "content-not-found")

    return content


async def validate_get_favourite(
    content_type: FavouriteContentTypeEnum,
    content: Anime = Depends(validate_content),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required()),
) -> Favourite:
    if not (
        favourite := await service.get_favourite(
            session, content_type, content, user
        )
    ):
        raise Abort("favourite", "not-found")

    return favourite


async def validate_add_favourite(
    content_type: FavouriteContentTypeEnum,
    session: AsyncSession = Depends(get_session),
    content: Anime = Depends(validate_content),
    user: User = Depends(auth_required()),
) -> Anime:
    if await service.get_favourite(session, content_type, content, user):
        raise Abort("favourite", "exists")

    return content
