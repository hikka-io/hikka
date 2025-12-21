from app.models.association import genres_anime_association_table
from app.models.association import genres_manga_association_table
from app.models.association import genres_novel_association_table
from app.common.utils import utc_to_kyiv, kyiv_to_utc, get_month
from datetime import datetime, timedelta, date
from app.models import User, History, Genre
from sqlalchemy import select, func, desc
from dataclasses import dataclass, field
from app.database import sessionmanager
from sqlalchemy.orm import joinedload
from app.utils import round_datetime
from app.utils import get_settings
from itertools import groupby
from app import constants
from enum import Enum
import asyncio
import json
import copy


# List of months because why not
MONTHS = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]


# Limit for top of completed titles
TOP_LIMIT = 3

# Limit of titles displayed per month
MONTHLY_DISPLAY_LIMIT = 10

# Min genre titles count in show in stats
MIN_GENRE_OCCURENCES = 3


class ContentType(str, Enum):
    ANIME = "anime"
    MANGA = "manga"
    NOVEL = "novel"


class Status(str, Enum):
    COMPLETED = "completed"
    PLANNED = "planned"
    DROPPED = "dropped"


@dataclass
class ContentEntry:
    complete_time: datetime | None = None
    total_episodes: int = 0
    total_chapters: int = 0
    total_volumes: int = 0
    new_watch: bool = False
    new_read: bool = False
    watch_count: int = 0
    read_count: int = 0
    rewatches: int = 0
    rereads: int = 0
    status: Status | None = None
    score: int | None = None
    title_score: float | None = None
    title_scored_by: int | None = None
    content_info: dict | None = None


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return int(obj.timestamp())
        elif isinstance(obj, date):
            return int(datetime.combine(obj, datetime.min.time()).timestamp())
        return super().default(obj)


def find_consecutive_days(datetimes, min_length=3):
    sorted_dates = sorted(datetimes)

    dates = [dt.date() for dt in sorted_dates]

    consecutive_groups = []
    for k, g in groupby(
        enumerate(dates), lambda x: x[1] - timedelta(days=x[0])
    ):
        group = list(g)
        if len(group) >= min_length:
            start_date = group[0][1]
            end_date = group[-1][1]
            consecutive_groups.append(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "count": len(group),
                }
            )

    return consecutive_groups


async def get_year_stats(session, history):
    # Here we hold bunch of temporary stuff
    status_cache = {}
    state_cache = {}
    days_cache = {}

    # This whould be returned by our function
    stats = {}

    DEFAULT_WATCH_ENTRY = {
        "complete_time": None,
        "total_episodes": 0,
        "new_watch": False,
        "watch_count": 0,
        "rewatches": 0,
        "status": None,
        "score": None,
        "title_score": None,
        "title_scored_by": None,
        "content": None,
    }

    DEFAULT_READ_ENTRY = {
        "complete_time": None,
        "total_chapters": 0,
        "total_volumes": 0,
        "new_read": False,
        "read_count": 0,
        "rereads": 0,
        "status": None,
        "score": None,
        "title_score": None,
        "title_scored_by": None,
        "content": None,
    }

    COMPLETED = "completed"
    PLANNED = "planned"
    DROPPED = "dropped"

    # List of anime watch statuses we build stats for
    TRACKED_STATUSES = [
        COMPLETED,
        PLANNED,
        DROPPED,
    ]

    # List of months why not
    MONTHS = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]

    # Function for initializing user data structures
    def init_user(user_ref):
        state_cache[user_ref] = {
            "anime": {},
            "manga": {},
            "novel": {},
        }

        stats[user_ref] = {
            "first_record": None,
            "last_record": None,
            "records_total": 0,
            "top": {"anime": [], "manga": [], "novel": []},
            "genres": {"anime": {}, "manga": {}, "novel": {}},
            "binges": [],
            "status": {
                "anime": {status: 0 for status in TRACKED_STATUSES},
                "manga": {status: 0 for status in TRACKED_STATUSES},
                "novel": {status: 0 for status in TRACKED_STATUSES},
            },
            "score": {
                "anime": {"min": None, "max": None, "avg": None},
                "manga": {"min": None, "max": None, "avg": None},
                "novel": {"min": None, "max": None, "avg": None},
            },
            "duration_total": 0,
            "duration_month": {month: 0 for month in MONTHS},
            "completed": {
                "anime": {month: [] for month in MONTHS},
                "manga": {month: [] for month in MONTHS},
                "novel": {month: [] for month in MONTHS},
            },
        }

        status_cache[user_ref] = {
            "anime": {status: [] for status in TRACKED_STATUSES},
            "manga": {status: [] for status in TRACKED_STATUSES},
            "novel": {status: [] for status in TRACKED_STATUSES},
        }

        days_cache[user_ref] = []

    # Function for updating cache of completed titles
    def update_status_cache(user_ref, content_type, content_id, status):
        if status in TRACKED_STATUSES:
            cache = status_cache[user_ref][content_type][status]
            if content_id not in cache:
                cache.append(content_id)

    # Counting completed titles
    def calculate_stats(user_ref):
        for content_type in status_cache[user_ref]:
            for status in TRACKED_STATUSES:
                count = len(status_cache[user_ref][content_type][status])
                stats[user_ref]["status"][content_type][status] = count

    # Main loop
    for record in history:
        content_type = {
            constants.HISTORY_WATCH: "anime",
            constants.HISTORY_READ_MANGA: "manga",
            constants.HISTORY_READ_NOVEL: "novel",
        }.get(record.history_type)

        if not content_type:
            continue

        month = get_month(record.created)

        entry = record.data
        if "after" not in entry:
            continue

        content = record.content
        user_ref = record.user.username
        content_ref = content.slug

        # NOTE: I hate this
        title_original = content_type != "anime"

        if user_ref not in state_cache:
            init_user(user_ref)

        user_state_cache = state_cache[user_ref][content_type]
        if content_ref not in user_state_cache:
            # We copy here because we don't want to overwite default template
            user_state_cache[content_ref] = copy.deepcopy(
                {
                    "anime": DEFAULT_WATCH_ENTRY,
                    "manga": DEFAULT_READ_ENTRY,
                    "novel": DEFAULT_READ_ENTRY,
                }.get(content_type)
            )

            user_state_cache[content_ref]["title_score"] = content.score
            user_state_cache[content_ref]["title_scored_by"] = content.scored_by
            user_state_cache[content_ref]["content"] = {
                "title_original"
                if title_original
                else "title_ja": content.title_original
                if title_original
                else content.title_ja,
                "title_en": content.title_en,
                "title_ua": content.title_ua,
                "image": content.image,
                "slug": content.slug,
            }

        # Building list of days of user activity to build binges later on
        record_day = round_datetime(utc_to_kyiv(record.created), 24, 60, 60)
        if record_day not in days_cache[user_ref]:
            days_cache[user_ref].append(record_day)

        # Bunch of variables for cleaner code
        tmp_state = user_state_cache[content_ref]
        before = entry.get("before", {})
        after = entry["after"]

        # Getting first and last records
        stats[user_ref]["last_record"] = record.created
        if stats[user_ref]["first_record"] is None:
            stats[user_ref]["first_record"] = record.created

        # Counting total
        stats[user_ref]["records_total"] += 1

        if entry.get("new_watch"):
            tmp_state["new_watch"] = True

        if entry.get("new_read"):
            tmp_state["new_read"] = True

        if "status" in after:
            # Here we only store single title completion
            # to prevent double storing rewarches
            if (
                tmp_state["status"] != COMPLETED
                and after["status"] == COMPLETED
                and content.id
                not in status_cache[user_ref][content_type][COMPLETED]
                and len(stats[user_ref]["completed"][content_type][month])
                < MONTHLY_DISPLAY_LIMIT
            ):
                stats[user_ref]["completed"][content_type][month].append(
                    {
                        (
                            "title_original" if title_original else "title_ja"
                        ): content.title_original
                        if title_original
                        else content.title_ja,
                        "title_en": content.title_en,
                        "title_ua": content.title_ua,
                        "date": record.created,
                        "image": content.image,
                        "slug": content.slug,
                    }
                )

                tmp_state["complete_time"] = record.created

            tmp_state["status"] = after["status"]
            update_status_cache(
                user_ref, content_type, content.id, after["status"]
            )

        else:
            tmp_state["status"] = PLANNED

        if "score" in after and after["score"] is not None:
            tmp_state["score"] = after["score"]

        if "rewatches" in after:
            tmp_state["rewatches"] = after["rewatches"]

        if "rereads" in after:
            tmp_state["rereads"] = after["rereads"]

        if "episodes" in after:
            current_eps = after["episodes"]
            before_eps = before.get("episodes") or 0

            # Reseting in case of rewarch
            if current_eps < before_eps:
                before_eps = 0

            # Calculating new episoded in history entry
            new_episodes = current_eps - before_eps
            tmp_state["total_episodes"] += new_episodes

            # If content has duration specidied
            # calculating user watch duration
            if content.duration:
                new_duration = new_episodes * content.duration
                stats[user_ref]["duration_total"] += new_duration
                stats[user_ref]["duration_month"][month] += new_duration

        volumes_changed = False
        if "volumes" in after:
            current_vol = after["volumes"]
            before_vol = before.get("volumes") or 0

            # Reseting in case of new volume
            if current_vol < before_vol:
                before_vol = 0

            if current_vol != before_vol:
                volumes_changed = True

            # Calculating new volumes in history entry
            new_volumes = current_vol - before_vol
            tmp_state["total_volumes"] += new_volumes

        if "chapters" in after:
            current_ch = after["chapters"]
            before_ch = before.get("chapters") or 0

            # Reseting in case of new volume
            if current_ch < before_ch or volumes_changed:
                before_ch = 0

            # Calculating new chapters in history entry
            new_chapters = current_ch - before_ch
            tmp_state["total_chapters"] += new_chapters

        if content_type == "anime":
            tmp_state["watch_count"] = 1 + tmp_state["rewatches"]
        else:
            tmp_state["read_count"] = 1 + tmp_state["rereads"]

    # Building genses cache so we don't do unnecessary queries
    genres = await session.scalars(select(Genre))
    genres_cache = {genre.id: genre.slug for genre in genres}

    # In this loop we build statistics per user
    for user_ref in status_cache:
        calculate_stats(user_ref)

        # Finding consecutive activity days aka binges
        stats[user_ref]["binges"] = find_consecutive_days(days_cache[user_ref])

        for content_type in status_cache[user_ref]:
            content_ids = list(
                set(
                    status_cache[user_ref][content_type]["planned"]
                    + status_cache[user_ref][content_type]["completed"]
                )
            )

            association_table = {
                "anime": genres_anime_association_table,
                "manga": genres_manga_association_table,
                "novel": genres_novel_association_table,
            }.get(content_type)

            association_content_id = {
                "anime": genres_anime_association_table.c.anime_id,
                "manga": genres_manga_association_table.c.manga_id,
                "novel": genres_novel_association_table.c.novel_id,
            }.get(content_type)

            # Maybe we can do that in single query?
            top_genres = await session.execute(
                select(
                    association_table.c.genre_id,
                    func.count(association_content_id).label("cnt"),
                )
                .filter(association_content_id.in_(content_ids))
                .group_by(association_table.c.genre_id)
                .order_by(desc("cnt"))
            )

            # Building top genres by titles stats
            for entry in top_genres:
                if entry.cnt < MIN_GENRE_OCCURENCES:
                    continue

                stats[user_ref]["genres"][content_type][
                    genres_cache.get(entry.genre_id)
                ] = entry.cnt

        min_score = None
        max_score = None
        avg_score = None
        total_score = 0
        score_count = 0

        for content_type in state_cache[user_ref]:
            for content_ref in state_cache[user_ref][content_type]:
                score = state_cache[user_ref][content_type][content_ref][
                    "score"
                ]

                if not score:
                    continue

                if min_score is None:
                    min_score = score

                if max_score is None:
                    max_score = score

                min_score = min(min_score, score)
                max_score = max(max_score, score)
                total_score += score
                score_count += 1

            if min_score and max_score:
                avg_score = round(total_score / score_count, 2)

            stats[user_ref]["score"][content_type]["min"] = min_score
            stats[user_ref]["score"][content_type]["max"] = max_score
            stats[user_ref]["score"][content_type]["avg"] = avg_score

        for content_type in state_cache[user_ref]:
            completed_records = {
                k: v
                for k, v in state_cache[user_ref][content_type].items()
                if v["complete_time"] is not None and v["score"] is not None
            }

            sorted_records = dict(
                sorted(
                    completed_records.items(),
                    key=lambda x: (
                        -x[1]["score"],
                        -x[1]["title_score"],
                        -x[1]["title_scored_by"],
                    ),
                )[:TOP_LIMIT]
            )

            for content_ref in sorted_records:
                entry = sorted_records[content_ref]
                stats[user_ref]["top"][content_type].append(
                    {"date": entry["complete_time"], "score": entry["score"]}
                    | entry["content"]
                )

    return stats


async def generate_year_artifact():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        start = kyiv_to_utc(datetime(2025, 1, 1))
        end = kyiv_to_utc(datetime(2026, 1, 1))

        volbil = await session.scalar(
            select(User).filter(User.username == "volbil")
        )

        olexh = await session.scalar(
            select(User).filter(User.username == "olexh")
        )

        okashi = await session.scalar(
            select(User).filter(User.username == "Okashi")
        )

        punpun = await session.scalar(
            select(User).filter(User.username == "punpun")
        )

        history = await session.scalars(
            select(History)
            .filter(
                History.created >= start,
                History.created < end,
                History.history_type.in_(
                    [
                        constants.HISTORY_WATCH,
                        constants.HISTORY_READ_MANGA,
                        constants.HISTORY_READ_NOVEL,
                    ]
                ),
                History.user_id.in_(
                    [
                        volbil.id,
                        olexh.id,
                        okashi.id,
                        punpun.id,
                    ]
                ),
            )
            .options(joinedload(History.user))
            .order_by(History.created.asc())
        )

        result = await get_year_stats(session, history)

        with open("year_data.json", "w") as file:
            json.dump(
                result, file, cls=DateTimeEncoder, indent=4, ensure_ascii=False
            )

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(generate_year_artifact())
