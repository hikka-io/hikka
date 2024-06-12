from sqlalchemy.ext.asyncio import AsyncSession
from app.service import get_content_by_slug
from .schemas import RelatedContentTypeEnum
from app.models import Anime, Manga, Novel
from app.database import get_session
from app.errors import Abort
from fastapi import Depends


async def verify_related_content(
    slug: str,
    content_type: RelatedContentTypeEnum,
    session: AsyncSession = Depends(get_session),
):
    if not (content := await get_content_by_slug(session, content_type, slug)):
        raise Abort("related", "content-not-found")

    return content


async def verify_content_franchise(
    content: Anime | Manga | Novel = Depends(verify_related_content),
):
    if content.franchise_id is None:
        raise Abort("related", "no-franchise")

    return content
