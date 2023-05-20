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
            select(Anime.content_id)
            .filter_by(needs_update=True)
            .order_by(desc("score"), desc("scored_by"))
            # .options(
            #     selectinload(Anime.studios),
            #     selectinload(Anime.producers),
            #     selectinload(Anime.genres),
            # )
            .limit(1)
        )

        print(anime)


# async def search_anime():
#     search = AnimeSearchArgs(
#         **{
#             # "query": "konosuba",
#             # "genres": ["comedy"],
#             # "rating": ["r_plus"],
#             # "source": ["light_novel"],
#             # "status": ["finished"],
#             # "season": ["summer"],
#         }
#     )

#     rating = [
#         f"rating = {rating}" for rating in enum_list_values(search.rating)
#     ]

#     status = [
#         f"status = {status}" for status in enum_list_values(search.status)
#     ]

#     source = [
#         f"source = {source}" for source in enum_list_values(search.source)
#     ]

#     season = [
#         f"season = {season}" for season in enum_list_values(search.season)
#     ]

#     producers = [f"producers = {producer}" for producer in search.producers]
#     studios = [f"studios = {studio}" for studio in search.studios]
#     genres = [f"genres = {genre}" for genre in search.genres]

#     year = []

#     if search.years[0]:
#         year.append([f"year>={search.years[0]}"])

#     if search.years[1]:
#         year.append([f"year<={search.years[1]}"])

#     query_filter = [
#         rating,
#         status,
#         source,
#         season,
#         genres,
#         producers,
#         studios,
#         year,
#     ]

#     query_filter = [entry for entry in query_filter if entry]

#     pprint(query_filter)

#     async with Client(**config.meilisearch) as client:
#         index = client.index("content_anime")

#         result = await index.search(
#             query=search.query,
#             page=search.page,
#             hits_per_page=12,
#             filter=query_filter,
#             sort=search.sort,
#         )

#         pprint(result)


if __name__ == "__main__":
    asyncio.run(test())
