from app.utils import get_settings
import aiohttp


async def get_anime_genres():
    settings = get_settings()

    endpoint = f"{settings.backend.aggregator}/genres/anime"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_manga_genres():
    settings = get_settings()

    endpoint = f"{settings.backend.aggregator}/genres/manga"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_roles(content_type):
    settings = get_settings()

    endpoint = f"{settings.backend.aggregator}/roles/{content_type}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_companies(page):
    settings = get_settings()

    endpoint = f"{settings.backend.aggregator}/companies?page={page}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_magazines(page):
    settings = get_settings()

    endpoint = f"{settings.backend.aggregator}/magazines?page={page}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_characters(page):
    settings = get_settings()

    endpoint = f"{settings.backend.aggregator}/characters?page={page}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_people(page):
    settings = get_settings()

    endpoint = f"{settings.backend.aggregator}/people?page={page}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_anime(page):
    settings = get_settings()

    endpoint = f"{settings.backend.aggregator}/anime?page={page}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_manga(page):
    settings = get_settings()

    endpoint = f"{settings.backend.aggregator}/manga?page={page}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_franchises(page):
    settings = get_settings()

    endpoint = f"{settings.backend.aggregator}/franchises?page={page}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_anime_info(content_id):
    settings = get_settings()

    endpoint = f"{settings.backend.aggregator}/anime/{content_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_manga_info(content_id):
    settings = get_settings()

    endpoint = f"{settings.backend.aggregator}/manga/{content_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data
