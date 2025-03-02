from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database import sessionmanager
from app.utils import get_settings
from zoneinfo import ZoneInfo
import asyncio

from app.sync import (
    delete_expired_token_requests,
    update_notifications,
    update_article_stats,
    update_ranking_all,
    update_aggregator,
    update_activity,
    update_schedule,
    update_ranking,
    update_history,
    update_sitemap,
    update_search,
    update_export,
    send_emails,
)


def init_scheduler():
    scheduler = AsyncIOScheduler()

    scheduler.add_job(delete_expired_token_requests, "interval", seconds=30)
    scheduler.add_job(update_notifications, "interval", seconds=10)
    scheduler.add_job(update_article_stats, "interval", minutes=1)
    scheduler.add_job(update_ranking_all, "interval", hours=1)
    scheduler.add_job(update_activity, "interval", seconds=10)
    scheduler.add_job(update_schedule, "interval", minutes=5)
    scheduler.add_job(update_ranking, "interval", seconds=10)
    scheduler.add_job(update_history, "interval", seconds=10)
    scheduler.add_job(update_export, "interval", minutes=1)
    scheduler.add_job(update_search, "interval", minutes=1)
    scheduler.add_job(send_emails, "interval", seconds=10)
    scheduler.add_job(update_sitemap, "interval", days=1)

    scheduler.add_job(
        update_aggregator,
        trigger=CronTrigger(
            timezone=ZoneInfo("Europe/Kyiv"),
            hour=1,
        ),
    )

    return scheduler


async def main():
    settings = get_settings()
    sessionmanager.init(settings.database.endpoint)

    scheduler = init_scheduler()

    try:
        scheduler.start()

        while True:
            await asyncio.sleep(1000)

    finally:
        await sessionmanager.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Stopped Hikka sync")
