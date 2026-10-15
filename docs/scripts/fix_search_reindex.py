from sqlalchemy import select, update, func
from app.database import sessionmanager
from app.utils import get_settings
from app.sync import update_search
import asyncio

from app.models import (
    Character,
    Company,
    Article,
    Person,
    Anime,
    Manga,
    Novel,
    User,
)


# Models which have their own Meilisearch index
SEARCH_MODELS = [Character, Company, Article, Person, Anime, Manga, Novel, User]


async def count_pending(session):
    total = 0

    for model in SEARCH_MODELS:
        total += await session.scalar(
            select(func.count(model.id)).filter(
                model.needs_search_update == True  # noqa: E712
            )
        )

    return total


async def fix_search_reindex():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        for model in SEARCH_MODELS:
            await session.execute(
                update(model).values(needs_search_update=True)
            )

        await session.commit()

        pending = await count_pending(session)

    # Search sync pages with offset over rows it marks as done so single
    # pass only gets through about half of them and we repeat it here
    while pending > 0:
        print(f"Reindexing, {pending} documents left")

        await update_search()

        async with sessionmanager.session() as session:
            left = await count_pending(session)

        # Drafts, system articles and manga without media type are never
        # pushed so we stop once a pass makes no progress
        if left >= pending:
            break

        pending = left

    print(f"Done, {pending} documents were not indexed")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_search_reindex())
