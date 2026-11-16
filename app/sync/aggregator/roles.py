from app.models import AnimeStaffRole, AuthorRole
from app.database import sessionmanager
from app import aggregator
from app import constants
from . import requests


async def aggregator_roles():
    async with sessionmanager.session() as session:
        data = await requests.get_roles(constants.CONTENT_ANIME)
        await aggregator.update_roles(session, AnimeStaffRole, data)

        data = await requests.get_roles(constants.CONTENT_MANGA)
        await aggregator.update_roles(session, AuthorRole, data)
