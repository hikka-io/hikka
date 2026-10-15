from app.settings.schemas import UserLink
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import User
import asyncio


async def fix_user_links():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        users = await session.scalars(select(User).filter(User.links != []))

        for user in users:
            # Icons are derived from link host now, so we rebuild links
            # through schema to replace icons picked by users before
            user.links = [
                UserLink(text=link.get("text"), url=link["url"]).model_dump(
                    mode="json"
                )
                for link in user.links
            ]

            if session.is_modified(user):
                print(f"Fixed links for {user.username}")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_user_links())
