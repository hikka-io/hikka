from app.aggregator.utils import send_telegram_notification
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
    update_search,
    # update_content,
)


async def import_aggregator():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await send_telegram_notification("Починаю синхронізацію з агрегатором")

    print("Genres")
    await send_telegram_notification("Синхронізую жанри...")
    await aggregator_genres()

    print("Roles")
    await send_telegram_notification("Синхронізую ролі...")
    await aggregator_roles()

    print("Characters")
    await send_telegram_notification("Синхронізую персонажів...")
    await aggregator_characters()

    print("Companies")
    await send_telegram_notification("Синхронізую компанії...")
    await aggregator_companies()

    print("Magazines")
    await send_telegram_notification("Синхронізую журнали...")
    await aggregator_magazines()

    print("People")
    await send_telegram_notification("Синхронізую людей...")
    await aggregator_people()

    print("Anime")
    await send_telegram_notification("Синхронізую аніме...")
    await aggregator_anime()

    print("Manga")
    await send_telegram_notification("Синхронізую манґу...")
    await aggregator_manga()

    print("Novel")
    await send_telegram_notification("Синхронізую ранобе...")
    await aggregator_novel()

    print("Anime info")
    await send_telegram_notification("Синхронізую інформацію про аніме...")
    await aggregator_anime_info()

    print("Manga info")
    await send_telegram_notification("Синхронізую інформацію про манґу...")
    await aggregator_manga_info()

    print("Novel info")
    await send_telegram_notification("Синхронізую інформацію про ранобе...")
    await aggregator_novel_info()

    print("Franchises")
    await send_telegram_notification("Синхронізую франшизи...")
    await aggregator_franchises()

    print("Schedule")
    await send_telegram_notification("Синхронізую календар...")
    await update_schedule_build()

    print("Search")
    await send_telegram_notification("Оновлюю пошук...")
    await update_search()

    # TODO: figure out what to do with deleted content
    # print("Content")
    # await update_content()

    # TODO: improve performance
    print("Weights")
    await send_telegram_notification("Перераховую ваги...")
    await update_weights()

    await send_telegram_notification("Готово!")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(import_aggregator())
