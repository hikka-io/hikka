from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Read, Manga, Novel, User
from app.dependencies import auth_required
from app.database import get_session
from app.errors import Abort
from fastapi import Depends

from app.service import get_content_by_slug
from . import service

from .schemas import (
    ReadContentTypeEnum,
    ReadArgs,
)


async def verify_read_content(
    slug: str,
    content_type: ReadContentTypeEnum,
    session: AsyncSession = Depends(get_session),
):
    if not (content := await get_content_by_slug(session, content_type, slug)):
        raise Abort("read", "content-not-found")

    return content


async def verify_read(
    content_type: ReadContentTypeEnum,
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
    content: Manga | Novel = Depends(verify_read_content),
) -> Read:
    if not (
        read := await service.get_read(
            session,
            content_type,
            content,
            user,
        )
    ):
        raise Abort("read", "not-found")

    return read


async def verify_add_read(
    args: ReadArgs,
    content: Manga | Novel = Depends(verify_read_content),
) -> Manga | Novel:
    # Make sure user provided chapters within constraints
    if content.chapters and args.chapters > content.chapters:
        raise Abort("read", "bad-chapters")

    # Make sure user provided volumes within constraints
    if content.volumes and args.volumes > content.volumes:
        raise Abort("read", "bad-volumes")

    return content
