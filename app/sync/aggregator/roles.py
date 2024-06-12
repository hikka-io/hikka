from app.database import sessionmanager
from app import aggregator
from app import constants
from . import requests


async def aggregator_roles():
    async with sessionmanager.session() as session:
        data = await requests.get_roles(constants.CONTENT_ANIME)
        await aggregator.update_anime_roles(session, data)

        data = await requests.get_roles(constants.CONTENT_MANGA)
        await aggregator.update_manga_roles(session, data)
