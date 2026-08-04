from app.common.service.duration import recalculate_watch_duration
from app.common.service.duration import recalculate_watch_stats
from app.database import sessionmanager


async def update_duration_and_stats():
    async with sessionmanager.session() as session:
        await recalculate_watch_duration(session)
        await recalculate_watch_stats(session)
