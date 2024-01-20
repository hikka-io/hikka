from .characters import update_search_characters
from .companies import update_search_companies
from .people import update_search_people
from app.database import sessionmanager
from .anime import update_search_anime
from app.utils import get_settings


async def update_search():
    await update_search_characters()
    await update_search_companies()
    await update_search_people()
    await update_search_anime()


async def update_search_task():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await update_search()

    await sessionmanager.close()
