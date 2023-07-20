from app import constants
import aiohttp


async def get_anime_genres():
    endpoint = f"{constants.AGGREGATOR}/genres/anime"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_anime_roles():
    endpoint = f"{constants.AGGREGATOR}/roles/anime"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_companies(page):
    endpoint = f"{constants.AGGREGATOR}/companies?page={page}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_characters(page):
    endpoint = f"{constants.AGGREGATOR}/characters?page={page}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_people(page):
    endpoint = f"{constants.AGGREGATOR}/people?page={page}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_anime(page):
    endpoint = f"{constants.AGGREGATOR}/anime?page={page}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_anime_franchises(page):
    endpoint = f"{constants.AGGREGATOR}/franchises/anime?page={page}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data


async def get_anime_info(content_id):
    endpoint = f"{constants.AGGREGATOR}/anime/{content_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data
