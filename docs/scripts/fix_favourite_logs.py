from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import Log
import asyncio


async def fix_favourite_logs():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        logs = await session.scalars(
            select(Log).filter(
                Log.log_type.in_(["favourite_add", "favourite_remove"])
            )
        )

        for log in logs:
            if "content_type" in log.data:
                continue

            log.data["content_type"] = "anime"

            session.add(log)
            await session.commit()

            print(f"Fixed log {log.id}")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_favourite_logs())
