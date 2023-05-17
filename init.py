from app.service import get_user_by_username
from app.database import sessionmanager
from app.models import Base, User
from sqlalchemy import select
from datetime import datetime
import asyncio
import config


async def create_db_and_tables():
    sessionmanager.init(config.database)

    async with sessionmanager.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(create_db_and_tables())
