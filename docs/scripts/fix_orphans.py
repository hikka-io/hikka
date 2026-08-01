from app.sync.orphans import resolve_orphaned_characters
from app.database import sessionmanager
from app.utils import get_settings
import asyncio


async def fix_orphans():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        await resolve_orphaned_characters(session)

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_orphans())
