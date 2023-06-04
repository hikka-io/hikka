from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import CompaniesSearchArgs
from sqlalchemy import select, desc
from app.models import Company
from sqlalchemy import func


async def search_total(session: AsyncSession):
    return await session.scalar(select(func.count(Company.id)))


async def companies_search(
    session: AsyncSession,
    limit: int,
    offset: int,
):
    query = select(Company).order_by(desc("favorites"), desc("content_id"))
    query = query.limit(limit).offset(offset)
    return await session.scalars(query)
