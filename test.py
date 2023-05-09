from meilisearch_python_async import Client
from pprint import pprint
import asyncio
import config


async def search():
    async with Client(**config.meilisearch) as client:
        index = client.index("content_anime")

        result = await index.search(query=None, page=1, hits_per_page=10)

        pprint(
            {
                "hits": len(result.hits),
                "hits_per_page": result.hits_per_page,
                "total_pages": result.total_pages,
                "total_hits": result.total_hits,
                "page": result.page,
            }
        )


if __name__ == "__main__":
    asyncio.run(search())
