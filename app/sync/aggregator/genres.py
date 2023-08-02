from app.database import sessionmanager
from app import aggregator
from . import requests


async def aggregator_anime_genres():
    async with sessionmanager.session() as session:
        data = await requests.get_anime_genres()
        await aggregator.save_anime_genres(session, data)
