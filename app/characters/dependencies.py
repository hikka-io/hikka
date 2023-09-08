from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Character
from app.errors import Abort
from fastapi import Depends
from . import service


# Get character by slug
async def get_character(
    slug: str, session: AsyncSession = Depends(get_session)
) -> Character:
    if not (character := await service.get_character_by_slug(session, slug)):
        raise Abort("character", "not-found")

    return character
