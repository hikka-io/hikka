from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import Log
import asyncio


async def fix_import_logs():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        logs = await session.scalars(
            select(Log).filter(Log.log_type == "settings_import")
        )

        for log in logs:
            log.log_type = "settings_import_watch"

            session.add(log)
            await session.commit()

            print(f"Fixed log {log.id}")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_import_logs())
