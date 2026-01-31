from meilisearch_python_sdk.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select, func
from app.utils import pagination
from app.models import Article
from app import constants
import math


async def update_article_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            filterable_attributes=["title"],
            searchable_attributes=["title"],
            displayed_attributes=[
                "title",
                "data_type",
                "slug",
            ],
            sortable_attributes=["title"],
            distinct_attribute="slug",
        )
    )


def article_to_document(article: Article):
    return {
        "data_type": "article",
        "id": article.content_id,
        "title": article.title,
        "slug": article.slug,
    }


async def article_documents(session: AsyncSession, limit: int, offset: int):
    article_list = await session.scalars(
        select(Article)
        .filter(Article.needs_search_update == True)  # noqa: E712
        .order_by("content_id")
        .limit(limit)
        .offset(offset)
    )

    documents = []

    for article in article_list:
        documents.append(article_to_document(article))
        article.needs_search_update = False
        session.add(article)

    return documents


async def article_documents_total(session: AsyncSession):
    return await session.scalar(
        select(func.count(Article.id)).filter(
            Article.needs_search_update == True  # noqa: E712
        )
    )


async def meilisearch_populate(session: AsyncSession):
    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_ARTICLES)

        await update_article_settings(index)

        size = 1000
        total = await article_documents_total(session)
        pages = math.ceil(total / size)

        for page in range(1, pages + 1):
            limit, offset = pagination(page, size)
            documents = await article_documents(session, limit, offset)

            await index.add_documents(documents)

            await session.commit()


async def update_search_article():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
