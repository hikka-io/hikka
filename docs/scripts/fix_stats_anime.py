from app.watch.service import generate_watch_stats
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import User
import asyncio


async def fix_stats():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        users = await session.scalars(select(User))

        for user in users:
            await generate_watch_stats(session, user)

            print(f"Generates list stats for {user.username}")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_stats())
