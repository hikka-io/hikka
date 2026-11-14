from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import update
from app.models import Article
from app import constants
import asyncio


async def fix_search_articles():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    # Old documents were keyed on related content id instead of article id
    # We drop whole index and let search sync build it again from scratch
    async with AsyncClient(**settings.meilisearch) as client:
        await client.delete_index_if_exists(constants.SEARCH_INDEX_ARTICLES)

    # Flag articles only after index is gone or sync running in between
    # could index them into old index and clear the flag
    async with sessionmanager.session() as session:
        await session.execute(update(Article).values(needs_search_update=True))
        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_search_articles())
