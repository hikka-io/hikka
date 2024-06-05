from app.database import sessionmanager
from app.utils import get_settings
import asyncio

from app.sync import (
    aggregator_franchises,
    update_schedule_build,
    aggregator_characters,
    aggregator_anime_info,
    aggregator_manga_info,
    aggregator_novel_info,
    aggregator_companies,
    aggregator_magazines,
    aggregator_genres,
    aggregator_people,
    aggregator_anime,
    aggregator_manga,
    aggregator_novel,
    aggregator_roles,
    update_weights,
    update_content,
    update_search,
)


async def import_aggregator():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    # await aggregator_genres()
    # await aggregator_roles()
    # await aggregator_characters()
    # await aggregator_companies()
    # await aggregator_magazines()
    # await aggregator_people()
    # await aggregator_anime()
    # await aggregator_manga()
    # await aggregator_novel()
    # await aggregator_anime_info()
    # await aggregator_manga_info()
    await aggregator_novel_info()
    # await aggregator_franchises()
    # await update_schedule_build()
    # await update_search()
    # await update_content()

    # TODO: improve performance
    # await update_weights()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(import_aggregator())
