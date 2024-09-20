from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import sessionmanager
from app.utils import get_settings
import asyncio

from app.sync import (
    delete_expired_token_requests,
    update_notifications,
    update_ranking_all,
    update_moderation,
    update_activity,
    update_schedule,
    update_ranking,
    update_history,
    update_sitemap,
    update_search,
    send_emails,
)


def init_scheduler():
    scheduler = AsyncIOScheduler()
    settings = get_settings()
    sessionmanager.init(settings.database.endpoint)

    scheduler.add_job(delete_expired_token_requests, "interval", seconds=30)
    scheduler.add_job(update_notifications, "interval", seconds=10)
    scheduler.add_job(update_moderation, "interval", seconds=10)
    scheduler.add_job(update_ranking_all, "interval", hours=1)
    scheduler.add_job(update_activity, "interval", seconds=10)
    scheduler.add_job(update_schedule, "interval", minutes=5)
    scheduler.add_job(update_ranking, "interval", seconds=10)
    scheduler.add_job(update_history, "interval", seconds=10)
    scheduler.add_job(update_search, "interval", minutes=1)
    scheduler.add_job(send_emails, "interval", seconds=10)
    scheduler.add_job(update_sitemap, "interval", days=1)
    scheduler.start()

    try:
        loop = asyncio.get_event_loop()
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        loop.run_until_complete(sessionmanager.close())
        loop.close()


if __name__ == "__main__":
    init_scheduler()
