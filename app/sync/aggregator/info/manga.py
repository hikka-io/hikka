from app.database import sessionmanager
from sqlalchemy.orm import joinedload
from sqlalchemy import select, desc
from app.models import Manga
from app import aggregator
from .. import requests
import asyncio


async def update_manga_info(semaphore, content_id):
    async with semaphore:
        async with sessionmanager.session() as session:
            manga = await session.scalar(
                select(Manga)
                .filter(Manga.content_id == content_id)
                .options(joinedload(Manga.magazines))
                .options(joinedload(Manga.genres))
            )

            data = await requests.get_manga_info(manga.content_id)

            await aggregator.update_manga_info(session, manga, data)


async def aggregator_manga_info():
    manga_list = []

    async with sessionmanager.session() as session:
        manga_list = await session.scalars(
            select(Manga.content_id)
            .filter(
                Manga.needs_update == True,  # noqa: E712
                Manga.deleted == False,  # noqa: E712
            )
            .order_by(desc("score"), desc("scored_by"))
        )

    semaphore = asyncio.Semaphore(5)

    tasks = [
        update_manga_info(semaphore, content_id) for content_id in manga_list
    ]

    await asyncio.gather(*tasks)
