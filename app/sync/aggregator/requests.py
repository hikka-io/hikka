from app.utils import get_settings
import aiohttp
import asyncio


async def request_aggregator(path):
    settings = get_settings()

    endpoint = f"{settings.backend.aggregator}{path}"

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            return await r.json()


async def get_all_pages(request):
    data = await request(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(5)

    async def make_request(page):
        async with semaphore:
            page_data = await request(page)
            return page_data["list"]

    # Page 1 is already fetched for the page count
    tasks = [make_request(page) for page in range(2, pages + 1)]
    result = await asyncio.gather(*tasks)

    return data["list"] + [item for sublist in result for item in sublist]


async def get_anime_genres():
    return await request_aggregator("/genres/anime")


async def get_manga_genres():
    return await request_aggregator("/genres/manga")


async def get_roles(content_type):
    return await request_aggregator(f"/roles/{content_type}")


async def get_companies(page):
    return await request_aggregator(f"/companies?page={page}")


async def get_magazines(page):
    return await request_aggregator(f"/magazines?page={page}")


async def get_characters(page):
    return await request_aggregator(f"/characters?page={page}")


async def get_people(page):
    return await request_aggregator(f"/people?page={page}")


async def get_anime(page):
    return await request_aggregator(f"/anime?page={page}")


async def get_manga(page):
    return await request_aggregator(f"/manga?page={page}")


async def get_novel(page):
    return await request_aggregator(f"/novel?page={page}")


async def get_franchises(page):
    return await request_aggregator(f"/franchises?page={page}")


async def get_anime_info(content_id):
    return await request_aggregator(f"/anime/{content_id}")


async def get_manga_info(content_id):
    return await request_aggregator(f"/manga/{content_id}")


async def get_novel_info(content_id):
    return await request_aggregator(f"/novel/{content_id}")
