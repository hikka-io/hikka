from app.database import sessionmanager
from app.utils import get_settings
from app.admin import service
import asyncio


async def send_system_notification():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        update_name = "customization_and_summary"
        # update_name = "delayed_devlog"

        # await service.delete_hikka_update_notification(session, update_name)

        await service.create_hikka_update_notification(
            session,
            update_name,
            "У цей святвечір ми принесли вам невеличке різдвяне оновлення.",
            "Кастомізація та підсумки року",
            "https://hikka.io/articles/kastomizatsiya-ta-pidsumky-roku-891dcf",
        )

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(send_system_notification())
