from app.sync import aggregator_anime_franchises
from app.sync import aggregator_anime_genres
from app.sync import aggregator_anime_info
from app.sync import aggregator_characters
from app.sync import aggregator_companies
from app.sync import aggregator_people
from app.sync import aggregator_anime
from app.sync import update_search
import asyncio

if __name__ == "__main__":
    # asyncio.run(aggregator_anime_genres())
    # asyncio.run(aggregator_characters())
    # asyncio.run(aggregator_companies())
    # asyncio.run(aggregator_people())
    # asyncio.run(aggregator_anime())
    # asyncio.run(aggregator_anime_info())
    # asyncio.run(aggregator_anime_franchises())
    asyncio.run(update_search())
