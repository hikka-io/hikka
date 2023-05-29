# from meilisearch_python_async.errors import MeiliSearchCommunicationError
# from meilisearch_python_async.errors import MeiliSearchApiError
# from meilisearch_python_async import Client
# from app.errors import Abort
# from typing import Union
# import asyncio
# import config

# from app.search.schemas import AnimeSearchArgs
# from app.search.utils import enum_list_values
# from pprint import pprint

from app.service import get_user_by_username
from app.models import Anime
from app.database import sessionmanager
from sqlalchemy import select, desc
from datetime import datetime
import asyncio
import config

from sqlalchemy.orm import selectinload


async def test():
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        anime = await session.scalar(
            select(Anime).order_by(desc("score"), desc("scored_by")).limit(1)
        )

        print(anime.poster)


if __name__ == "__main__":
    asyncio.run(test())
