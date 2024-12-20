from app.database import sessionmanager
from app.utils import get_settings
from app.admin import service
import asyncio


async def send_system_notification():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        update_name = "hikka_snow"

        # await service.delete_hikka_update_notification(session, update_name)

        await service.create_hikka_update_notification(
            session,
            update_name,
            "В налаштуваннях кастомізації можна ввімкнути сніжинки!",
            "Святковий настрій ❄️",
            "https://hikka.io/settings/customization",
        )

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(send_system_notification())
