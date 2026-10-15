from meilisearch_python_sdk.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from app.utils import get_settings
from app.models import Article
from sqlalchemy import select
from app import constants
from uuid import UUID


async def update_article_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            filterable_attributes=["title"],
            searchable_attributes=["title"],
            displayed_attributes=["title", "slug", "reference"],
            sortable_attributes=["title"],
            distinct_attribute="slug",
        )
    )


def article_to_document(article: Article):
    return {
        "reference": article.reference,
        "id": str(article.content_id),
        "title": article.title,
        "slug": article.slug,
    }


async def article_documents(
    session: AsyncSession, limit: int, last_id: UUID | None
):
    query = (
        select(Article)
        .filter(
            Article.category != constants.ARTICLE_SYSTEM,
            Article.needs_search_update == True,  # noqa: E712
            Article.deleted == False,  # noqa: E712
            Article.draft == False,  # noqa: E712
        )
        .order_by(Article.id)
        .limit(limit)
    )

    # Rows drop out of the filter once indexed so we page by key
    if last_id:
        query = query.filter(Article.id > last_id)

    article_list = await session.scalars(query)

    article_list = article_list.unique().all()
    documents = []

    for article in article_list:
        documents.append(article_to_document(article))
        last_id = article.id
        article.needs_search_update = False
        session.add(article)

    return documents, last_id


async def meilisearch_populate(session: AsyncSession):
    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_ARTICLES)

        await update_article_settings(index)

        size = 1000
        last_id = None

        while True:
            documents, last_id = await article_documents(session, size, last_id)

            if len(documents) == 0:
                break

            await index.add_documents(documents, primary_key="id")

            await session.commit()


async def update_search_article():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
