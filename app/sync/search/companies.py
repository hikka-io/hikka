from meilisearch_python_sdk.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from app.settings import get_settings
from sqlalchemy import select, func
from app.utils import pagination
from app.models import Company
from app import constants
import math


async def update_companies_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            filterable_attributes=["favorites"],
            searchable_attributes=["name"],
            displayed_attributes=[
                "image",
                "name",
                "slug",
            ],
            sortable_attributes=["favorites"],
            distinct_attribute="slug",
        )
    )


async def companies_documents(session: AsyncSession, limit: int, offset: int):
    companies_list = await session.scalars(
        select(Company).order_by("content_id").limit(limit).offset(offset)
    )

    documents = [
        {
            "favorites": company.favorites,
            "id": company.content_id,
            "image": company.image,
            "name": company.name,
            "slug": company.slug,
        }
        for company in companies_list
    ]

    return documents


async def companies_documents_total(session: AsyncSession):
    return await session.scalar(select(func.count(Company.id)))


async def meilisearch_populate(session: AsyncSession):
    print("Meilisearch: Populating companies")

    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_COMPANIES)

        await update_companies_settings(index)

        size = 1000
        total = await companies_documents_total(session)
        pages = math.ceil(total / size)

        for page in range(1, pages + 1):
            print(f"Meilisearch: Processing companies page {page}")

            limit, offset = pagination(page, size)
            documents = await companies_documents(session, limit, offset)

            await index.add_documents(documents)


async def update_search_companies():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
