from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import sessionmanager
from app.sync import update_sitemap
from app.sync import update_search
from app.utils import get_settings
from app.sync import send_emails
import asyncio


def init_scheduler():
    scheduler = AsyncIOScheduler()
    settings = get_settings()
    sessionmanager.init(settings.database.endpoint)

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
