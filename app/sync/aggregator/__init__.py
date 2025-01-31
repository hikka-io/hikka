from .franchises import aggregator_franchises
from .characters import aggregator_characters
from .info.anime import aggregator_anime_info
from .info.manga import aggregator_manga_info
from .info.novel import aggregator_novel_info
from .companies import aggregator_companies
from .magazines import aggregator_magazines
from .schedule import update_schedule_build
from .people import aggregator_people
from .genres import aggregator_genres
from .anime import aggregator_anime
from .manga import aggregator_manga
from .novel import aggregator_novel
from .roles import aggregator_roles
from .weights import update_weights

from app.aggregator.utils import (
    send_telegram_notification,
    update_telegram_message,
    SyncTracker,
)


async def update_aggregator():
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
