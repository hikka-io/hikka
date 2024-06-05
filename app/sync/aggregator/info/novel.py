from app.database import sessionmanager
from sqlalchemy.orm import joinedload
from sqlalchemy import select, desc
from app.models import Novel
from app import aggregator
from .. import requests
import asyncio


async def update_novel_info(semaphore, content_id):
    async with semaphore:
        async with sessionmanager.session() as session:
            novel = await session.scalar(
                select(Novel)
                .filter(Novel.content_id == content_id)
                .options(joinedload(Novel.magazines))
                .options(joinedload(Novel.genres))
            )

            data = await requests.get_novel_info(novel.content_id)

            await aggregator.update_novel_info(session, novel, data)


async def aggregator_novel_info():
    novel_list = []

    async with sessionmanager.session() as session:
        novel_list = await session.scalars(
            select(Novel.content_id)
            .filter(
                Novel.needs_update == True,  # noqa: E712
                Novel.deleted == False,  # noqa: E712
            )
            .order_by(desc("score"), desc("scored_by"))
        )

    semaphore = asyncio.Semaphore(10)

    tasks = [
        update_novel_info(semaphore, content_id) for content_id in novel_list
    ]

    await asyncio.gather(*tasks)
