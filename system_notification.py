from app.admin.service import create_hikka_update_notification
from app.database import sessionmanager
from app.utils import get_settings
import asyncio


async def send_system_notification():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        update_name = "hikka_snow"

        await create_hikka_update_notification(
            session,
            update_name,
            "Якщо вам не вистачає святкового настрою, то в налаштуваннях кастомізації можна ввімкнути сніжинки!",
            "Святковий настрій ❄️",
            "https://hikka.io/settings/customization",
        )

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(send_system_notification())
