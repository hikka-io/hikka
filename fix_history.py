from app.database import sessionmanager
from app.utils import get_settings
from app.models import History
from sqlalchemy import select
from app import constants
import asyncio
import copy


async def migrate_history():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        history_list = await session.scalars(
            select(History).filter(
                History.history_type == constants.HISTORY_WATCH
            )
        )

        for history in history_list:
            history.data = copy.deepcopy(history.data)

            if "note" in history.data["before"]:
                history.data["before"].pop("note")

            if "note" in history.data["after"]:
                history.data["after"].pop("note")

            if history.data["before"] == {} and history.data["after"] == {}:
                print(f"Deleting {history.reference} history record")
                await session.delete(history)

            else:
                if session.is_modified(history):
                    print(f"Updating {history.reference} history record")
                    session.add(history)

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(migrate_history())
