from sqlalchemy import select, func, asc, cast, Date, text
from datetime import datetime, timezone
from app.database import sessionmanager
from app.utils import get_settings
from app.models import User, Log
import asyncio


GRANULARITY_STEP = {
    "day": "1 day",
    "week": "1 week",
    "month": "1 month",
}


def date_to_timestamp(d):
    return int(
        datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp()
    )


async def get_registration_stats(session, granularity="day", compound=False):
    step = text(f"interval '{GRANULARITY_STEP[granularity]}'")
    result = []

    kyiv_created = func.timezone(
        "Europe/Kyiv", func.timezone("UTC", User.created)
    )

    period = func.date_trunc(granularity, kyiv_created)

    stats = (
        select(
            period.label("date"),
            func.count(User.id).label("count"),
        )
        .group_by("date")
        .cte("stats")
    )

    bounds = select(
        func.min(stats.c.date).label("min_date"),
        func.max(stats.c.date).label("max_date"),
    ).subquery()

    periods = select(
        cast(
            func.generate_series(
                bounds.c.min_date,
                bounds.c.max_date,
                step,
            ),
            Date,
        ).label("period")
    ).subquery()

    entries = await session.execute(
        select(
            periods.c.period.label("date"),
            func.coalesce(stats.c.count, 0).label("count"),
        )
        .select_from(periods)
        .outerjoin(stats, stats.c.date == periods.c.period)
        .order_by(asc(periods.c.period))
    )

    total = 0

    for entry in entries:
        total += entry.count

        result.append(
            {
                "timestamp": date_to_timestamp(entry.date),
                "users": total if compound else entry.count,
            }
        )

    return result


async def get_activity_stats(session, granularity):
    step = text(f"interval '{GRANULARITY_STEP[granularity]}'")
    result = []

    kyiv_created = func.timezone(
        "Europe/Kyiv", func.timezone("UTC", Log.created)
    )

    period = func.date_trunc(granularity, kyiv_created)

    stats = (
        select(
            period.label("date"),
            func.count(Log.user_id.distinct()).label("count"),
        )
        .group_by("date")
        .cte("stats")
    )

    bounds = select(
        func.min(stats.c.date).label("min_date"),
        func.max(stats.c.date).label("max_date"),
    ).subquery()

    periods = select(
        cast(
            func.generate_series(
                bounds.c.min_date,
                bounds.c.max_date,
                step,
            ),
            Date,
        ).label("period")
    ).subquery()

    entries = await session.execute(
        select(
            periods.c.period.label("date"),
            func.coalesce(stats.c.count, 0).label("count"),
        )
        .select_from(periods)
        .outerjoin(stats, stats.c.date == periods.c.period)
        .order_by(asc(periods.c.period))
    )

    for entry in entries:
        result.append(
            {
                "timestamp": date_to_timestamp(entry.date),
                "users": entry.count,
            }
        )

    return result


async def fix_generate_stats():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        # for granularity in GRANULARITY_STEP:
        #     result = await get_registration_stats(session, granularity)

        #     print(granularity)
        #     print(result)
        #     print("\n\n")

        # for granularity in GRANULARITY_STEP:
        #     result = await get_registration_stats(session, granularity, True)

        #     print(granularity, "compound")
        #     print(result)
        #     print("\n\n")

        for granularity in GRANULARITY_STEP:
            result = await get_activity_stats(session, granularity)

            print(granularity)
            print(result)
            print("\n\n")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_generate_stats())
