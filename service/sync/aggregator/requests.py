from service import constants
import aiohttp

async def get_anime_genres():
    endpoint = f"{constants.AGGREGATOR}/genres/anime"

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

async def get_characters(page, results=None):
    endpoint = f"{constants.AGGREGATOR}/characters?page={page}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            data = await r.json()
            return data
