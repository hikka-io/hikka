from app.sync.export import get_export_data
from app.database import sessionmanager
from app.models import User, UserExport
from app.utils import get_settings
from sqlalchemy import select
from app.utils import utcnow
import asyncio


async def fix_export():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        # Getting users which interacted with their list
        users = await session.scalars(select(User))

        now = utcnow()

        # And generating export record for them
        for user in users:
            exported_list = await get_export_data(session, user.id)

            if not (
                export := await session.scalar(
                    select(UserExport).filter(UserExport.user == user)
                )
            ):
                export = UserExport(
                    **{
                        "created": now,
                        "updated": now,
                        "user": user,
                    }
                )

            export.anime = exported_list["anime"]
            export.manga = exported_list["manga"]
            export.novel = exported_list["novel"]
            export.updated = now

            session.add(export)

            print(f"Generated export for {user.username}")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_export())
