from service.sync import aggregator_anime_genres
from service.sync import aggregator_characters
from service.sync import aggregator_companies
import asyncio

if __name__ == "__main__":
    # asyncio.run(aggregator_anime_genres())
    asyncio.run(aggregator_characters())
    # asyncio.run(aggregator_companies())
