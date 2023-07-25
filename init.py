from app.database import sessionmanager
from app.settings import get_settings
from app.models import Base
import asyncio


async def create_db_and_tables():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoin)

    async with sessionmanager.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await sessionmanager.close()


asyncio.run(create_db_and_tables())
