from meilisearch_python_sdk.errors import MeilisearchCommunicationError
from .characters import update_search_characters
from .companies import update_search_companies
from .article import update_search_article
from .people import update_search_people
from app.database import sessionmanager
from .anime import update_search_anime
from .manga import update_search_manga
from .novel import update_search_novel
from .users import update_search_users
from sqlalchemy import select, func
from app import constants


async def update_search():
    """Update Meilisearch with new data"""

    # Ensure only one runs at the time
    async with sessionmanager.session() as lock_session:
        if not await lock_session.scalar(
            select(
                func.pg_try_advisory_xact_lock(
                    constants.ADVISORY_LOCK_SEARCH_SYNC
                )
            )
        ):
            print("Meilisearch: update is already running, skipping")
            return

        try:
            await update_search_characters()
            await update_search_companies()
            await update_search_article()
            await update_search_people()
            await update_search_anime()
            await update_search_manga()
            await update_search_novel()
            await update_search_users()

        except MeilisearchCommunicationError as e:
            print(f"Meilisearch is down:\n{e}")
