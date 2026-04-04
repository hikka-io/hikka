from app.database import sessionmanager
from app.utils import get_settings
from app.admin import service
import asyncio


async def send_system_notification():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        update_name = "feed_customization"
        # update_name = "customization_and_summary"
        # update_name = "delayed_devlog"

        # await service.delete_hikka_update_notification(session, update_name)

        await service.create_hikka_update_notification(
            session,
            update_name,
            "Робимо роботу над помилками після оновлення головної сторінки.",
            "Макет сторінки та фільтри стрічки",
            "https://hikka.io/articles/maket-storinky-ta-filtry-strichky-dd38cd",
        )

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(send_system_notification())
