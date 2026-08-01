from app.database import sessionmanager
from app.utils import get_settings
from app.admin import service
import asyncio


async def send_system_notification():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        update_name = "reviews_and_quality_of_life"
        # update_name = "customization_and_summary"
        # update_name = "delayed_devlog"

        # await service.delete_hikka_update_notification(session, update_name)

        await service.create_hikka_update_notification(
            session,
            update_name,
            "Розповідаємо про систему відгуків та інші покращення на сайті",
            "Система відгуків та інші покращення",
            "https://hikka.io/articles/systema-vidhukiv-ta-inshi-pokrashchennya-yakosti-zhyttya-b97e83",
        )

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(send_system_notification())
