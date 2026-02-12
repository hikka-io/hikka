from meilisearch_python_sdk.errors import MeilisearchCommunicationError
from .characters import update_search_characters
from .companies import update_search_companies
from .article import update_search_article
from .people import update_search_people
from .anime import update_search_anime
from .manga import update_search_manga
from .novel import update_search_novel
from .users import update_search_users


async def update_search():
    """Update Meilisearch with new data"""

    try:
        await update_search_characters()
        await update_search_companies()
        await update_search_article()
        await update_search_people()
        await update_search_anime()
        await update_search_manga()
        await update_search_novel()
        await update_search_users()

    except MeilisearchCommunicationError:
        print("Meilisearch is down")
