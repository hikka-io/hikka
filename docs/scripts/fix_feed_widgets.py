from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import User
import asyncio
import copy


async def fix_feed_widgets():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        users = await session.scalars(select(User))

        for user in users:
            if "feed" in user.preferences:
                if "widgets" in user.preferences["feed"]:
                    user.preferences = copy.deepcopy(user.preferences)
                    user.preferences["feed"].pop("widgets")
                    print(f"Updated user {user.username}")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_feed_widgets())
