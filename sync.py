from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio


def init_scheduler():
    scheduler = AsyncIOScheduler()

    from app.sync import send_emails

    scheduler.add_job(send_emails, "interval", seconds=10)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    init_scheduler()
