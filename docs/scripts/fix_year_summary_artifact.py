from app.sync import digest_year_summary
from app.database import sessionmanager
from app.utils import get_settings
import asyncio


async def generate_year_digest():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await digest_year_summary()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(generate_year_digest())
