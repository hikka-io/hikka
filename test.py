from meilisearch_python_async import Client
from app.utils import get_season
from tortoise import Tortoise
from app.models import Anime
from pprint import pprint
import asyncio
import config


# async def search():
#     async with Client(**config.meilisearch) as client:
#         index = client.index("content_anime")

#         result = await index.search(query=None, page=1, hits_per_page=10)

#         pprint(
#             {
#                 "hits": len(result.hits),
#                 "hits_per_page": result.hits_per_page,
#                 "total_pages": result.total_pages,
#                 "total_hits": result.total_hits,
#                 "page": result.page,
#             }
#         )


async def fix_year():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    anime_list = await Anime.filter()

    for anime in anime_list:
        season = get_season(anime.start_date)
        year = anime.start_date.year if anime.start_date else None

        anime.season = season
        anime.year = year

        await anime.save()

        print(
            f"Updated anime {anime.title_ja} with season {season} and year {year}"
        )


if __name__ == "__main__":
    asyncio.run(fix_year())
