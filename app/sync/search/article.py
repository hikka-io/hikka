from meilisearch_python_sdk.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select, or_
from app.models import Article
from app import constants
from uuid import UUID


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
    # Rows stay locked until the batch is committed so edits made
    # meanwhile wait and flag the row again instead of being overwritten
    # Drafts are indexed too so authors can search them, articles list
    # decides who can see what
    query = (
        select(Article)
        .filter(
            Article.category != constants.ARTICLE_SYSTEM,
            Article.needs_search_update == True,  # noqa: E712
            Article.deleted == False,  # noqa: E712
        )
        .order_by(Article.id)
        .limit(limit)
        .with_for_update(of=Article, skip_locked=True)
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


async def article_document_ids_delete(session: AsyncSession):
    article_list = await session.scalars(
        select(Article)
        .filter(
            or_(
                Article.category == constants.ARTICLE_SYSTEM,
                Article.deleted == True,  # noqa: E712
            ),
            Article.needs_search_update == True,  # noqa: E712
        )
        .with_for_update(of=Article, skip_locked=True)
    )

    delete_ids = []

    for article in article_list.unique():
        delete_ids.append(article.reference)
        article.needs_search_update = False
        session.add(article)

    return delete_ids


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

        delete_document_ids = await article_document_ids_delete(session)

        if len(delete_document_ids) > 0:
            await index.delete_documents(delete_document_ids)
            print(
                f"Meilisearch: deleted {len(delete_document_ids)} articles from search"
            )

        await session.commit()


async def update_search_article():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
