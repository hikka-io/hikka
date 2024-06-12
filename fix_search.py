from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import update
import asyncio

from app.models import (
    Character,
    Person,
    Anime,
    Manga,
    Novel,
    User,
)


async def fix_aggregator():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        await session.execute(update(Person).values(needs_search_update=True))
        await session.execute(update(Anime).values(needs_search_update=True))
        await session.execute(update(Manga).values(needs_search_update=True))
        await session.execute(update(Novel).values(needs_search_update=True))
        await session.execute(update(User).values(needs_search_update=True))
        await session.execute(
            update(Character).values(needs_search_update=True)
        )

        await session.execute(update(Anime).values(needs_search_update=True))
        await session.execute(update(Manga).values(needs_search_update=True))
        await session.execute(update(Novel).values(needs_search_update=True))

        await session.commit()

        print("Reset aggregator and search")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_aggregator())
