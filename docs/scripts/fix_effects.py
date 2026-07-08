from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import User
import asyncio
import copy


async def fix_effects():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        users = await session.scalars(select(User))

        for user in users:
            if (
                "effects" in user.preferences
                and "effect" not in user.preferences
                and user.preferences["effects"] is not None
                and len(user.preferences["effects"]) > 0
            ):
                user.preferences = copy.deepcopy(user.preferences)
                user.preferences["effect"] = user.preferences["effects"][0]
                print(f"Updated user {user.username}")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_effects())
