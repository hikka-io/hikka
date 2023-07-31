from app.database import sessionmanager
from app.settings import get_settings
from app.models import Base
import asyncio


async def create_db_and_tables():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(create_db_and_tables())
