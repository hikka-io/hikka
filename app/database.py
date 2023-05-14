from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import async_sessionmaker

# ToDo: move to config
engine = create_async_engine(
    "postgresql+asyncpg://dev:password@localhost:5432/hikka",
    future=True,
    echo=True,
)

# async_session = async_sessionmaker(engine, expire_on_commit=False)


# expire_on_commit=False will prevent attributes from being expired
# after commit.
AsyncSessionFactory = sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


# Dependency
async def get_db():
    async with AsyncSessionFactory() as session:
        yield session
