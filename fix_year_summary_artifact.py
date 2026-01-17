from app.sync import artifact_year_summary
from app.database import sessionmanager
from app.utils import get_settings
import asyncio


async def generate_year_artifact():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await artifact_year_summary()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(generate_year_artifact())
