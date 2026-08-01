from app.sync.score import update_scores
from app.database import sessionmanager
from app.utils import get_settings
import asyncio


async def fix_weighted_scores():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await update_scores()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_weighted_scores())
