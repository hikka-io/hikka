from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Person
from app.errors import Abort
from fastapi import Depends
from . import service


# Get person by slug
async def get_person(
    slug: str, session: AsyncSession = Depends(get_session)
) -> Person:
    if not (person := await service.get_person_by_slug(session, slug)):
        raise Abort("person", "not-found")

    return person
