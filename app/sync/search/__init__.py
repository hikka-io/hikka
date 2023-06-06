from .characters import update_search_characters
from .companies import update_search_companies
from .people import update_search_people
from .anime import update_search_anime


async def update_search():
    await update_search_characters()
    await update_search_companies()
    await update_search_people()
    await update_search_anime()
