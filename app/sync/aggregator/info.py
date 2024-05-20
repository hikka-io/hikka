from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from sqlalchemy import select, desc
from app.models import Anime
from app import aggregator
from . import requests
import asyncio


async def update_anime_info(semaphore, content_id):
    async with semaphore:
        async with sessionmanager.session() as session:
            anime = await session.scalar(
                select(Anime)
                .filter(Anime.content_id == content_id)
                .options(selectinload(Anime.genres))
            )

            data = await requests.get_anime_info(anime.content_id)

            await aggregator.update_anime_info(session, anime, data)


async def aggregator_anime_info():
    anime_list = []

    async with sessionmanager.session() as session:
        anime_list = await session.scalars(
            select(Anime.content_id)
            .filter(
                Anime.needs_update == True,  # noqa: E712
                Anime.deleted == False,  # noqa: E712
            )
            .order_by(desc("score"), desc("scored_by"))
        )

    semaphore = asyncio.Semaphore(10)

    tasks = [
        update_anime_info(semaphore, content_id) for content_id in anime_list
    ]

    await asyncio.gather(*tasks)
