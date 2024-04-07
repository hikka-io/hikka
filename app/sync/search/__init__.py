from .characters import update_search_characters
from .companies import update_search_companies
from .people import update_search_people
from .anime import update_search_anime
from .users import update_search_users


async def update_search():
    """Update Meilisearch with new data"""

    await update_search_characters()
    await update_search_companies()
    await update_search_people()
    await update_search_anime()
    await update_search_users()
