from typing import AsyncIterator
import contextlib

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncConnection,
    AsyncSession,
    AsyncEngine,
)


# import logging

# # Create a logger instance
# logger = logging.getLogger("sqlalchemy.engine")
# logger.setLevel(logging.ERROR)

# # Create a file handler and set its level
# file_handler = logging.FileHandler("sqlalchemy.log")
# file_handler.setLevel(logging.ERROR)

# # Create a formatter and add it to the file handler
# formatter = logging.Formatter(
#     "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# file_handler.setFormatter(formatter)

# # Add the file handler to the logger
# logger.addHandler(file_handler)


class DatabaseSessionManager:
    def __init__(self):
        self._sessionmaker: async_sessionmaker | None = None
        self._engine: AsyncEngine | None = None

    def init(self, host: str):
        self._engine = create_async_engine(host, echo=False)
        self._sessionmaker = async_sessionmaker(
            autocommit=False,
            expire_on_commit=False,
            bind=self._engine,
        )

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        await self._engine.dispose()

        self._sessionmaker = None
        self._engine = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()

        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager()


async def get_session():
    async with sessionmanager.session() as session:
        yield session
