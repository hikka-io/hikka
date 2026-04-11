from app.database import sessionmanager
from app.utils import get_settings
from app.admin import service
import asyncio


async def send_system_notification():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        update_name = "sakura_effect"
        # update_name = "customization_and_summary"
        # update_name = "delayed_devlog"

        # await service.delete_hikka_update_notification(session, update_name)

        await service.create_hikka_update_notification(
            session,
            update_name,
            "Доступно в налаштуваннях кастомізації вашого профілю",
            "Весна прийшла на сайт, сакура зацвіла 🌸",
            "https://hikka.io/settings/customization",
        )

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(send_system_notification())
