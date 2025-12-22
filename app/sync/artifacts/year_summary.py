from app.models.association import genres_anime_association_table
from app.models.association import genres_manga_association_table
from app.models.association import genres_novel_association_table
from app.common.utils import utc_to_kyiv, kyiv_to_utc, get_month
from .utils import DateTimeEncoder, find_consecutive_days
from sqlalchemy.dialects.postgresql import insert
from app.models import Artifact, History, Genre
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import round_datetime, utcnow
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
from app.database import sessionmanager
from sqlalchemy.orm import joinedload
from app import constants
import json
import copy


# Limit for top of completed titles
TOP_LIMIT = 3

# Limit genres stats to 6
TOP_GENRES_LIMIT = 6

# Limit of titles displayed per month
MONTHLY_DISPLAY_LIMIT = 20

# Min genre titles count in show in stats
MIN_GENRE_OCCURENCES = 3

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


class YearStatsGenerator:
    def __init__(self, session: AsyncSession, history: list):
        self.session = session
        self.history = history

        # Here we hold bunch of temporary stuff
        self.activity_days = {}
        self.status_cache = {}
        self.state_cache = {}

        # Final result
        self.stats = {}

    async def calculate(self):
        self._process_history()

        for user_ref in self.status_cache:
            self._calculate_stats(user_ref)
            self._calculate_binges(user_ref)
            self._calculate_scores(user_ref)
            self._calculate_top(user_ref)

            await self._find_top_genres(user_ref)

        return self.stats

    async def _find_top_genres(self, user_ref):
        # Building genses cache so we don't do unnecessary queries
        genres = await self.session.scalars(select(Genre))
        genres_cache = {
            genre.id: {
                "name_ua": genre.name_ua,
                "name_en": genre.name_en,
                "slug": genre.slug,
            }
            for genre in genres
        }

        for content_type in self.status_cache[user_ref]:
            content_ids = list(
                set(
                    self.status_cache[user_ref][content_type]["planned"]
                    + self.status_cache[user_ref][content_type]["completed"]
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
            top_genres = await self.session.execute(
                select(
                    association_table.c.genre_id,
                    func.count(association_content_id).label("cnt"),
                )
                .filter(association_content_id.in_(content_ids))
                .group_by(association_table.c.genre_id)
                .order_by(desc("cnt"))
                .limit(TOP_GENRES_LIMIT)
            )

            # Building top genres by titles stats
            for entry in top_genres:
                if entry.cnt < MIN_GENRE_OCCURENCES:
                    continue

                genre_entry = genres_cache.get(entry.genre_id)
                self.stats[user_ref]["genres"][content_type].append(
                    genre_entry | {"count": entry.cnt}
                )

    def _calculate_top(self, user_ref):
        for content_type in self.state_cache[user_ref]:
            completed_records = {
                k: v
                for k, v in self.state_cache[user_ref][content_type].items()
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
                self.stats[user_ref]["top"][content_type].append(
                    {"date": entry["complete_time"], "score": entry["score"]}
                    | entry["content"]
                )

    def _calculate_scores(self, user_ref):
        min_score = None
        max_score = None
        avg_score = None
        total_score = 0
        score_count = 0

        for content_type in self.state_cache[user_ref]:
            for content_ref in self.state_cache[user_ref][content_type]:
                score = self.state_cache[user_ref][content_type][content_ref][
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

            self.stats[user_ref]["score"][content_type]["min"] = min_score
            self.stats[user_ref]["score"][content_type]["max"] = max_score
            self.stats[user_ref]["score"][content_type]["avg"] = avg_score

    def _calculate_binges(self, user_ref):
        # Finding consecutive activity days aka binges
        self.stats[user_ref]["binges"] = find_consecutive_days(
            self.activity_days[user_ref]
        )

    def _calculate_stats(self, user_ref):
        for content_type in self.status_cache[user_ref]:
            for status in TRACKED_STATUSES:
                count = len(self.status_cache[user_ref][content_type][status])
                self.stats[user_ref]["status"][content_type][status] = count

    def _process_history(self):
        for record in self.history:
            content_type = {
                constants.HISTORY_WATCH: "anime",
                constants.HISTORY_READ_MANGA: "manga",
                constants.HISTORY_READ_NOVEL: "novel",
            }.get(record.history_type)

            if not content_type:
                continue

            if "after" not in record.data:
                continue

            self._process_record(record, content_type)

    # Function for initializing user data structures
    def _init_user(self, user_ref):
        if user_ref in self.state_cache:
            return

        self.state_cache[user_ref] = {
            "anime": {},
            "manga": {},
            "novel": {},
        }

        self.stats[user_ref] = {
            "first_record": None,
            "last_record": None,
            "records_total": 0,
            "top": {"anime": [], "manga": [], "novel": []},
            "genres": {"anime": [], "manga": [], "novel": []},
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
            "completed_count": {
                "anime": {month: 0 for month in MONTHS},
                "manga": {month: 0 for month in MONTHS},
                "novel": {month: 0 for month in MONTHS},
            },
        }

        self.status_cache[user_ref] = {
            "anime": {status: [] for status in TRACKED_STATUSES},
            "manga": {status: [] for status in TRACKED_STATUSES},
            "novel": {status: [] for status in TRACKED_STATUSES},
        }

        self.activity_days[user_ref] = []

    def _init_content(self, user_ref, content_ref, content_type, content):
        user_state_cache = self.state_cache[user_ref][content_type]
        if content_ref in user_state_cache:
            return

        # We copy here because we don't want to overwite default template
        user_state_cache[content_ref] = copy.deepcopy(
            {
                "anime": DEFAULT_WATCH_ENTRY,
                "manga": DEFAULT_READ_ENTRY,
                "novel": DEFAULT_READ_ENTRY,
            }.get(content_type)
        )

        # NOTE: I hate this
        title_original = content_type != "anime"

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

    def _track_activity_day(self, user_ref, created):
        # Building list of days of user activity to build binges later on
        record_day = round_datetime(utc_to_kyiv(created), 24, 60, 60)
        if record_day not in self.activity_days[user_ref]:
            self.activity_days[user_ref].append(record_day)

    def _update_record_timestamps(self, user_ref, created):
        # Getting first and last records
        self.stats[user_ref]["last_record"] = created
        if self.stats[user_ref]["first_record"] is None:
            self.stats[user_ref]["first_record"] = created

    def _process_content_update(
        self,
        user_ref,
        content_ref,
        content_type,
        content,
        history_entry,
        created,
    ):
        month = get_month(created)

        # Bunch of variables for cleaner code
        tmp_state = self.state_cache[user_ref][content_type][content_ref]

        before = history_entry.get("before", {})
        after = history_entry["after"]

        # NOTE: I hate this
        title_original = content_type != "anime"

        if history_entry.get("new_watch"):
            tmp_state["new_watch"] = True

        if history_entry.get("new_read"):
            tmp_state["new_read"] = True

        if "status" in after:
            # Here we only store single title completion
            # to prevent double storing rewarches
            if (
                tmp_state["status"] != COMPLETED
                and after["status"] == COMPLETED
                and content.id
                not in self.status_cache[user_ref][content_type][COMPLETED]
            ):
                self.stats[user_ref]["completed_count"][content_type][
                    month
                ] += 1

                if (
                    len(self.stats[user_ref]["completed"][content_type][month])
                    < MONTHLY_DISPLAY_LIMIT
                ):
                    self.stats[user_ref]["completed"][content_type][
                        month
                    ].append(
                        {
                            (
                                "title_original"
                                if title_original
                                else "title_ja"
                            ): content.title_original
                            if title_original
                            else content.title_ja,
                            "title_en": content.title_en,
                            "title_ua": content.title_ua,
                            "image": content.image,
                            "slug": content.slug,
                            "date": created,
                        }
                    )

                    tmp_state["complete_time"] = created

            tmp_state["status"] = after["status"]

            status = after["status"]
            if status in TRACKED_STATUSES:
                cache = self.status_cache[user_ref][content_type][status]
                if content.id not in cache:
                    cache.append(content.id)

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

                # TODO: Calculate separately and handle deletes
                self.stats[user_ref]["duration_total"] += new_duration

                self.stats[user_ref]["duration_month"][month] += new_duration

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

    def _process_record(self, record, content_type):
        # content_ref = record.content.slug
        # user_ref = record.user.username
        content_ref = str(record.target_id)
        user_ref = str(record.user_id)
        history_entry = record.data
        content = record.content

        self._init_user(user_ref)
        self._init_content(user_ref, content_ref, content_type, content)
        self._track_activity_day(user_ref, record.created)
        self._update_record_timestamps(user_ref, record.created)

        # Counting total
        self.stats[user_ref]["records_total"] += 1

        self._process_content_update(
            user_ref,
            content_ref,
            content_type,
            content,
            history_entry,
            record.created,
        )


async def artifact_year_summary():
    async with sessionmanager.session() as session:
        start = kyiv_to_utc(datetime(2025, 1, 1))
        end = kyiv_to_utc(datetime(2026, 1, 1))
        artifact_name = "year-summary-2025"
        now = utcnow()

        # We should stop generating after 1 day of end period
        if now > end + timedelta(days=1):
            return

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
            )
            .options(joinedload(History.user))
            .order_by(History.created.asc())
        )

        generator = YearStatsGenerator(session, history)
        result = await generator.calculate()

        for user_id in result:
            data = json.loads(json.dumps(result[user_id], cls=DateTimeEncoder))

            await session.execute(
                insert(Artifact)
                .values(
                    name=artifact_name,
                    user_id=user_id,
                    created=now,
                    updated=now,
                    data=data,
                )
                .on_conflict_do_update(
                    index_elements=["user_id", "name"],
                    set_={
                        "updated": now,
                        "data": data,
                    },
                )
            )

        await session.commit()
