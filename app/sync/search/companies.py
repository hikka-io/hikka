from meilisearch_python_async.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_async import Client
from app.database import sessionmanager
from app.models import Company
from sqlalchemy import select
from app import constants
import config


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


async def companies_documents(session: AsyncSession):
    companies_list = await session.scalars(select(Company))

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


async def meilisearch_populate(session: AsyncSession):
    print("Meilisearch: Populating companies")

    documents = await companies_documents(session)

    async with Client(**config.meilisearch) as client:
        index = client.index(constants.COMPANIES_SEARCH_INDEX)

        await update_companies_settings(index)

        await index.add_documents(documents)


async def update_search_companies():
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
