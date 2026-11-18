from meilisearch_python_sdk.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select, or_
from app.models import Article
from app import constants
from uuid import UUID
from . import service


async def update_article_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            searchable_attributes=["title"],
            displayed_attributes=["id", "title", "slug"],
        )
    )


def article_to_document(article: Article):
    return {
        "id": article.reference,
        "title": article.title,
        "slug": article.slug,
    }


async def article_documents(
    session: AsyncSession, limit: int, last_id: UUID | None
):
    # Drafts are indexed too so authors can search them, articles list
    # decides who can see what
    query = select(Article).filter(
        Article.category != constants.ARTICLE_SYSTEM,
        Article.needs_search_update == True,  # noqa: E712
        Article.deleted == False,  # noqa: E712
    )

    return await service.get_documents(
        session, query, Article.id, article_to_document, limit, last_id
    )


async def article_document_ids_delete(session: AsyncSession):
    query = select(Article).filter(
        or_(
            Article.category == constants.ARTICLE_SYSTEM,
            Article.deleted == True,  # noqa: E712
        ),
        Article.needs_search_update == True,  # noqa: E712
    )

    return await service.get_delete_ids(session, query, Article.id)


async def update_search_article():
    settings = get_settings()

    async with sessionmanager.session() as session:
        async with AsyncClient(**settings.meilisearch) as client:
            index = client.index(constants.SEARCH_INDEX_ARTICLES)

            await update_article_settings(index)

            await service.index_documents(
                session, index, article_documents, primary_key="id"
            )

            await service.delete_documents(
                session, index, article_document_ids_delete
            )
