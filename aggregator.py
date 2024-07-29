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

    print("Genres")
    await aggregator_genres()
    print("Roles")
    await aggregator_roles()
    print("Characters")
    await aggregator_characters()
    print("Companies")
    await aggregator_companies()
    print("Magazines")
    await aggregator_magazines()
    print("People")
    await aggregator_people()
    print("Anime")
    await aggregator_anime()
    print("Manga")
    await aggregator_manga()
    print("Novel")
    await aggregator_novel()
    print("Anime info")
    await aggregator_anime_info()
    print("Manga info")
    await aggregator_manga_info()
    print("Novel info")
    await aggregator_novel_info()
    print("Franchises")
    await aggregator_franchises()
    print("Schedule")
    await update_schedule_build()
    print("Search")
    await update_search()
    print("Content")
    await update_content()

    # TODO: improve performance
    print("Weights")
    await update_weights()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(import_aggregator())
