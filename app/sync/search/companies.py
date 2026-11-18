from meilisearch_python_sdk.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from sqlalchemy.orm import with_expression
from app.database import sessionmanager
from sqlalchemy import select, case
from app.utils import get_settings
from app.models import Company
from app import constants
from . import service


async def update_companies_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            filterable_attributes=["favorites", "is_studio", "is_producer"],
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


def company_to_document(company: Company):
    return {
        "is_studio": company.is_studio,
        "is_producer": company.is_producer,
        "favorites": company.favorites,
        "id": company.content_id,
        "image": company.image,
        "name": company.name,
        "slug": company.slug,
    }


async def companies_documents(
    session: AsyncSession, limit: int, last_id: str | None
):
    query = (
        select(Company)
        .filter(Company.needs_search_update == True)  # noqa: E712
        .options(
            with_expression(
                Company.is_studio,
                case((Company.studio_anime.any(), True), else_=False),
            )
        )
        .options(
            with_expression(
                Company.is_producer,
                case((Company.produced_anime.any(), True), else_=False),
            )
        )
    )

    return await service.get_documents(
        session, query, Company.content_id, company_to_document, limit, last_id
    )


async def update_search_companies():
    settings = get_settings()

    async with sessionmanager.session() as session:
        async with AsyncClient(**settings.meilisearch) as client:
            index = client.index(constants.SEARCH_INDEX_COMPANIES)

            await update_companies_settings(index)

            await service.index_documents(session, index, companies_documents)
