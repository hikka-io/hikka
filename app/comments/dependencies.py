from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import ContentTypeEnum
from app.database import get_session
from app.errors import Abort
from fastapi import Depends
from . import service


async def validate_content_slug(
    slug: str,
    content_type: ContentTypeEnum,
    session: AsyncSession = Depends(get_session),
) -> str:
    if not (
        content := await service.get_content_by_slug(
            session, content_type, slug
        )
    ):
        raise Abort("comment", "content-not-found")

    return content.reference
