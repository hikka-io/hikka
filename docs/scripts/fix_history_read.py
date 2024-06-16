from app.database import sessionmanager
from app.utils import get_settings
from app.models import History
from sqlalchemy import select
import asyncio


async def fix_history_read():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        history_list = await session.scalars(
            select(History).filter(
                History.history_type.in_(
                    ["manga", "novel", "manga_delete", "novel_delete"]
                )
            )
        )

        for history in history_list:
            if history.history_type.startswith("read_"):
                continue

            history.history_type = "read_" + history.history_type
            session.add(history)
            await session.commit()

            print(f"Fixed history {history.id}")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_history_read())
