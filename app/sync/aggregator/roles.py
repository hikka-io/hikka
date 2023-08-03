from app.database import sessionmanager
from app import aggregator
from . import requests


async def aggregator_anime_roles():
    async with sessionmanager.session() as session:
        data = await requests.get_anime_roles()
        await aggregator.update_anime_roles(session, data)
