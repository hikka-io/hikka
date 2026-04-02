from app.database import sessionmanager
from app.utils import get_settings
from app.admin import service
import asyncio


async def send_system_notification():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        update_name = "feed_and_design"
        # update_name = "customization_and_summary"
        # update_name = "delayed_devlog"

        # await service.delete_hikka_update_notification(session, update_name)

        await service.create_hikka_update_notification(
            session,
            update_name,
            "Розповідаємо про оновлену головну сторінку та покращений дизайн.",
            "Стрічка та оновлений дизайн",
            "https://hikka.io/articles/strichka-ta-onovlenyy-dyzayn-e9997b",
        )

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(send_system_notification())
