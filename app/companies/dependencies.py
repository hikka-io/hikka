from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Company
from app.errors import Abort
from fastapi import Depends
from . import service


# Get company by slug
async def get_company(
    slug: str, session: AsyncSession = Depends(get_session)
) -> Company:
    if not (company := await service.get_company_by_slug(session, slug)):
        raise Abort("company", "not-found")

    return company
