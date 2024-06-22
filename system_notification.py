from app.admin.service import create_hikka_update_notification
from app.database import sessionmanager
from app.utils import get_settings
import asyncio


async def send_system_notification():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        update_name = "hikka_manga_update"

        await create_hikka_update_notification(
            session,
            update_name,
            "Розповідаємо про нові розділи сайту з манґою та ранобе",
            "Манґа, ранобе та список читання",
            "https://t.me/hikka_io/25",
        )

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(send_system_notification())
