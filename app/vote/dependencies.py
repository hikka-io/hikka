from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Anime, User, Favourite
from app.service import get_content_by_slug
from app.dependencies import auth_required
from app.database import get_session
from .schemas import ContentTypeEnum
from app.errors import Abort
from fastapi import Depends
from . import service


async def validate_content(
    slug: str,
    content_type: ContentTypeEnum,
    session: AsyncSession = Depends(get_session),
) -> Anime:
    if not (content := await get_content_by_slug(session, content_type, slug)):
        raise Abort("vote", "content-not-found")

    return content


async def validate_get_vote(
    content_type: ContentTypeEnum,
    content: Anime = Depends(validate_content),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required()),
) -> Favourite:
    if not (
        vote := await service.get_vote(session, content_type, content, user)
    ):
        raise Abort("vote", "not-found")

    return vote
