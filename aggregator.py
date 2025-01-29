from app.aggregator.utils import send_telegram_notification
from app.aggregator.utils import update_telegram_message
from app.aggregator.utils import SyncTracker
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

    tracker = SyncTracker()

    print("Genres")
    tracker.add_task(["Синхронізую жанри", "Синхронізувала жанри"])
    message_id = await send_telegram_notification(tracker.get_status_message())
    await aggregator_genres()

    print("Roles")
    tracker.add_task(["Синхронізую ролі", "Синхронізувала ролі"])
    await update_telegram_message(message_id, tracker.get_status_message())
    await aggregator_roles()

    print("Characters")
    tracker.add_task(["Синхронізую персонажів", "Синхронізувала персонажів"])
    await update_telegram_message(message_id, tracker.get_status_message())
    await aggregator_characters()

    print("Companies")
    tracker.add_task(["Синхронізую компанії", "Синхронізувала компанії"])
    await update_telegram_message(message_id, tracker.get_status_message())
    await aggregator_companies()

    print("Magazines")
    tracker.add_task(["Синхронізую журнали", "Синхронізувала журнали"])
    await update_telegram_message(message_id, tracker.get_status_message())
    await aggregator_magazines()

    print("People")
    tracker.add_task(["Синхронізую людей", "Синхронізувала людей"])
    await update_telegram_message(message_id, tracker.get_status_message())
    await aggregator_people()

    print("Anime")
    tracker.add_task(["Синхронізую аніме", "Синхронізувала аніме"])
    await update_telegram_message(message_id, tracker.get_status_message())
    await aggregator_anime()

    print("Manga")
    tracker.add_task(["Синхронізую манґу", "Синхронізувала манґу"])
    await update_telegram_message(message_id, tracker.get_status_message())
    await aggregator_manga()

    print("Novel")
    tracker.add_task(["Синхронізую ранобе", "Синхронізувала ранобе"])
    await update_telegram_message(message_id, tracker.get_status_message())
    await aggregator_novel()

    print("Anime info")
    tracker.add_task(
        [
            "Синхронізую інформацію про аніме",
            "Синхронізувала інформацію про аніме",
        ]
    )
    await update_telegram_message(message_id, tracker.get_status_message())
    await aggregator_anime_info()

    print("Manga info")
    tracker.add_task(
        [
            "Синхронізую інформацію про манґу",
            "Синхронізувала інформацію про манґу",
        ]
    )
    await update_telegram_message(message_id, tracker.get_status_message())
    await aggregator_manga_info()

    print("Novel info")
    tracker.add_task(
        [
            "Синхронізую інформацію про ранобе",
            "Синхронізувала інформацію про ранобе",
        ]
    )
    await update_telegram_message(message_id, tracker.get_status_message())
    await aggregator_novel_info()

    print("Franchises")
    tracker.add_task(["Синхронізую франшизи", "Синхронізувала франшизи"])
    await update_telegram_message(message_id, tracker.get_status_message())
    await aggregator_franchises()

    print("Schedule")
    tracker.add_task(["Синхронізую календар", "Синхронізувала календар"])
    await update_telegram_message(message_id, tracker.get_status_message())
    await update_schedule_build()

    print("Search")
    tracker.add_task(["Оновлюю пошук", "Оновила пошук"])
    await update_telegram_message(message_id, tracker.get_status_message())
    await update_search()

    # TODO: figure out what to do with deleted content
    # print("Content")
    # await update_content()

    # TODO: improve performance
    print("Weights")
    tracker.add_task(["Перераховую ваги", "Перерахувала ваги"])
    await update_telegram_message(message_id, tracker.get_status_message())
    await update_weights()

    await update_telegram_message(message_id, tracker.get_final_message())

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(import_aggregator())
