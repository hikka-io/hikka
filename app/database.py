from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
import config

engine = create_async_engine(config.database, future=True, echo=True)

AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


# Dependency
async def get_session():
    async with AsyncSessionFactory() as session:
        yield session
