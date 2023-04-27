from service.sync import aggregator_anime_genres
from service.sync import aggregator_anime_info
from service.sync import aggregator_characters
from service.sync import aggregator_companies
from service.sync import aggregator_people
from service.sync import aggregator_anime
import asyncio

if __name__ == "__main__":
    # asyncio.run(aggregator_anime_genres())
    # asyncio.run(aggregator_characters())
    # asyncio.run(aggregator_companies())
    # asyncio.run(aggregator_people())
    # asyncio.run(aggregator_anime())
    asyncio.run(aggregator_anime_info())
