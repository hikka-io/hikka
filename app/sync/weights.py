from app.database import sessionmanager
from app import aggregator


async def update_weights():
    async with sessionmanager.session() as session:
        await aggregator.update_anime_staff_weights(session)
