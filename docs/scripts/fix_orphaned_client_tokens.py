from sqlalchemy import select, update, func
from app.database import sessionmanager
from app.utils import get_settings
from app.models import AuthToken
from app.utils import utcnow
import asyncio


async def fix_orphaned_client_tokens():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        now = utcnow()

        # Hard deleting client used to set client_id to null on its tokens
        # but they kept their scope (first party tokens never have one)
        orphaned = [
            AuthToken.client_id == None,  # noqa: E711
            AuthToken.scope != [],
            AuthToken.expiration > now,
        ]

        total = await session.scalar(
            select(func.count(AuthToken.id)).filter(*orphaned)
        )

        await session.execute(
            update(AuthToken).filter(*orphaned).values(expiration=now)
        )

        await session.commit()

        print(f"Expired {total} orphaned client tokens")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_orphaned_client_tokens())
