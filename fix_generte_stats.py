from sqlalchemy import select, func, asc, cast, Date, text, Integer
from app.models import User, Log, Anime
from app.database import sessionmanager
from datetime import datetime, timezone
from app.utils import get_settings
from app import constants
import asyncio


GRANULARITY_STEP = {
    "day": "1 day",
    "week": "1 week",
    "month": "1 month",
}

# Only these logs carry episode/rewatch changes in their data field.
# Note that list imports write one settings_import_watch log instead,
# so imported titles never show up in the watch time series.
WATCH_LOG_TYPES = [
    constants.LOG_WATCH_CREATE,
    constants.LOG_WATCH_UPDATE,
]


def date_to_timestamp(d):
    return int(
        datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp()
    )


def granularity_step(granularity):
    # The step goes into raw SQL so it must never come from the caller
    if granularity not in GRANULARITY_STEP:
        raise ValueError(f"Bad granularity: {granularity}")

    return text(f"interval '{GRANULARITY_STEP[granularity]}'")


def period_column(column, granularity):
    # Our timestamps are naive UTC, so we mark them as UTC first
    # and only then convert them to Kyiv time
    return func.date_trunc(
        granularity,
        func.timezone("Europe/Kyiv", func.timezone("UTC", column)),
    )


async def collect_periods(
    session, stats, step, compound=False, key="users"
):
    """
    Take a CTE with date/count columns, add the periods with no rows
    and return a list of dicts.
    """

    # Bounds come from values that are already cut into periods,
    # so the series always lines up with the buckets
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

    result = []
    total = 0

    for entry in entries:
        total += entry.count

        result.append(
            {
                "timestamp": date_to_timestamp(entry.date),
                key: total if compound else entry.count,
            }
        )

    return result


async def get_registration_stats(session, granularity="day", compound=False):
    step = granularity_step(granularity)
    period = period_column(User.created, granularity)

    stats = (
        select(
            period.label("date"),
            func.count(User.id).label("count"),
        )
        .group_by("date")
        .cte("stats")
    )

    return await collect_periods(session, stats, step, compound)


async def get_activity_stats(session, granularity="day"):
    # NOTE: distinct user counts do not add up between periods.
    # The month value is monthly active users, not the sum of the days.
    # For the same reason there is no compound option here.
    step = granularity_step(granularity)
    period = period_column(Log.created, granularity)

    stats = (
        select(
            period.label("date"),
            func.count(Log.user_id.distinct()).label("count"),
        )
        .group_by("date")
        .cte("stats")
    )

    return await collect_periods(session, stats, step)


def watch_field(side, field):
    # A field shows up in the diff only when it changes.
    # On watch_create the before side is always null.
    return func.coalesce(
        Log.data[side][field].astext.cast(Integer), 0
    )


def watch_delta(field):
    return watch_field("after", field) - watch_field("before", field)


def watch_minutes():
    # Same formula as watch_duration in app/common/service/duration.py,
    # but applied to the change instead of the whole record.
    # We drop negative deltas because a user who lowers a count
    # corrects a mistake, they do not unwatch anything.
    return func.coalesce(Anime.duration, 0) * (
        func.greatest(watch_delta("episodes"), 0)
        + func.coalesce(Anime.episodes_total, 0)
        * func.greatest(watch_delta("rewatches"), 0)
    )


async def get_watch_time_stats(session, granularity="day", compound=False):
    step = granularity_step(granularity)
    period = period_column(Log.created, granularity)

    stats = (
        select(
            period.label("date"),
            func.coalesce(func.sum(watch_minutes()), 0).label("count"),
        )
        .join(Anime, Anime.id == Log.target_id)
        .filter(Log.log_type.in_(WATCH_LOG_TYPES))
        .group_by("date")
        .cte("stats")
    )

    return await collect_periods(
        session, stats, step, compound, key="minutes"
    )


async def fix_generate_stats():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        for granularity in GRANULARITY_STEP:
            result = await get_watch_time_stats(session, granularity)

            print(granularity)
            print(result[-5:])
            print("\n\n")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_generate_stats())
