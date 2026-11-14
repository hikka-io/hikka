from app.common.schemas.novel import NovelSearchArgs
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Novel
from app.errors import Abort
from fastapi import Depends

from app.common.service.read_content import (
    validate_read_content_search_args,
    get_read_content_info_by_slug,
    get_read_content_by_slug,
    novel_models,
)


# Get novel by slug
async def valdidate_novel_info(
    slug: str, session: AsyncSession = Depends(get_session)
) -> Novel:
    if not (
        novel := await get_read_content_info_by_slug(
            session, novel_models, slug
        )
    ):
        raise Abort("novel", "not-found")

    return novel


async def validate_novel(
    slug: str, session: AsyncSession = Depends(get_session)
):
    if not (
        novel := await get_read_content_by_slug(session, novel_models, slug)
    ):
        raise Abort("novel", "not-found")

    return novel


async def validate_search_novel(
    search: NovelSearchArgs,
    session: AsyncSession = Depends(get_session),
) -> NovelSearchArgs:
    await validate_read_content_search_args(session, novel_models, search)
    return search
