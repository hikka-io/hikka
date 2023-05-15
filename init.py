from app.database import engine, AsyncSessionFactory
from app.models import Base, User
import asyncio


async def test():
    async with AsyncSessionFactory() as session:
        session.add(User(name="volbil"))
        await session.commit()


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(create_db_and_tables())
# asyncio.run(test())
