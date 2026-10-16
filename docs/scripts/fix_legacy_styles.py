from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import text
import asyncio


async def fix_legacy_styles():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        # Legacy themes and typography were removed from UIStyles and
        # response model rejects unknown keys so we strip them from users
        result = await session.execute(
            text(
                "UPDATE service_users "
                "SET styles = styles - 'light' - 'dark' - 'typography' "
                "WHERE styles ?| array['light', 'dark', 'typography']"
            )
        )

        print(f"Stripped legacy style keys for {result.rowcount} users")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_legacy_styles())
