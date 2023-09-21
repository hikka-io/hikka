from app.database import sessionmanager
from app.settings import get_settings
import asyncio

from app.sync import (
    # aggregator_anime_franchises,
    # aggregator_anime_genres,
    # aggregator_anime_roles,
    # aggregator_characters,
    # aggregator_anime_info,
    # aggregator_companies,
    # aggregator_people,
    # aggregator_anime,
    update_search,
)


async def import_aggregator():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    # await aggregator_anime_genres()
    # await aggregator_anime_roles()
    # await aggregator_characters()
    # await aggregator_companies()
    # await aggregator_people()
    # await aggregator_anime()
    # await aggregator_anime_info()
    # await aggregator_anime_franchises()
    await update_search()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(import_aggregator())
