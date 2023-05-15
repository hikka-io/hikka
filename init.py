from app.service import get_user_by_username
from app.database import sessionmanager
from app.models import Base, User
from sqlalchemy import select
from datetime import datetime
import asyncio
import config


async def create_user(session) -> User:
    now = datetime.utcnow()

    user = User(
        **{
            "banned": False,
            "activated": True,
            "email": "volbilnexus@gmail.com",
            "password_hash": "HASH",
            "username": "volbil",
            "last_active": now,
            "created": now,
            "login": now,
        }
    )

    session.add(user)

    await session.commit()

    return user


async def test():
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        user = await create_user(session)
        print(user.username)
        # session.add(create_user())
        # await session.commit()

        # if user := await get_user_by_username("volbil", session):
        #     print(user.username)


async def create_db_and_tables():
    sessionmanager.init(config.database)

    async with sessionmanager.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(create_db_and_tables())
# asyncio.run(test())
