from app.database import sessionmanager
from sqlalchemy.orm import joinedload
from app.service import create_log
from app.utils import get_settings
from app.models import Log, User
from zoneinfo import ZoneInfo
from datetime import datetime
from sqlalchemy import select
from app import constants
import asyncio
import copy
import json

APPLY = False

STYLE_FIELDS = [
    "backdrop",
    "brand",
    "light",
    "dark",
    "overrides",
    "typography",
    "radius",
]

FEED_LIST_FIELDS = [
    "collection_content_types",
    "comment_content_types",
    "article_content_types",
    "review_content_types",
    "article_categories",
    "feed_content_types",
]

FRONTEND_DEFAULT_WIDGETS = [
    {"side": "left", "slug": "profile", "order": 1},
    {"side": "left", "slug": "list", "order": 2},
    {"side": "left", "slug": "collections", "order": 3},
    {"side": "right", "slug": "tracker", "order": 1},
    {"side": "right", "slug": "history", "order": 2},
    {"side": "right", "slug": "articles", "order": 3},
    {"side": "right", "slug": "schedule", "order": 4},
    {"side": "center", "slug": "ongoings", "order": 1},
    {"side": "center", "slug": "feed", "order": 2},
]

# Incident window
WINDOW_START = datetime(2026, 7, 8, 22, 50)
WINDOW_END = datetime(2026, 7, 9, 15, 0)


def kyiv_to_utc(naive_kyiv):
    aware_kyiv = naive_kyiv.replace(tzinfo=ZoneInfo("Europe/Kyiv"))
    aware_utc = aware_kyiv.astimezone(ZoneInfo("UTC"))
    return aware_utc.replace(tzinfo=None)


def is_empty(value):
    return value is None or value == {} or value == []


def widgets_key(widgets):
    if not widgets:
        return None
    return sorted((w["side"], w["slug"], w["order"]) for w in widgets)


DEFAULT_WIDGETS_KEY = widgets_key(FRONTEND_DEFAULT_WIDGETS)


async def fix_preferences():
    settings = get_settings()
    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        logs = await session.scalars(
            select(Log)
            .filter(
                Log.log_type == constants.LOG_SETTINGS_CUSTOMIZATION,
                Log.created > kyiv_to_utc(WINDOW_START),
                Log.created < kyiv_to_utc(WINDOW_END),
            )
            .options(joinedload(Log.user))
            .order_by(Log.created.asc())
        )

        baseline = {}

        for log in logs:
            if log.user_id in baseline:
                continue

            before = log.data.get("before") or {}
            baseline[log.user_id] = (
                log.user.username,
                before.get("styles") or {},
                before.get("preferences") or {},
            )

        restored_any = False

        for user_id, (username, good_styles, good_prefs) in baseline.items():
            user = await session.get(User, user_id)
            if user is None:
                continue

            styles = copy.deepcopy(user.styles or {})
            prefs = copy.deepcopy(user.preferences or {})
            good_feed = good_prefs.get("feed") or {}
            feed = prefs.get("feed") or {}
            recovered = []

            for field in STYLE_FIELDS:
                good_val = good_styles.get(field)
                if is_empty(good_val) or not is_empty(styles.get(field)):
                    continue
                styles[field] = good_val
                recovered.append(f"styles.{field}")

            for field in FEED_LIST_FIELDS:
                good_val = good_feed.get(field)
                if is_empty(good_val) or not is_empty(feed.get(field)):
                    continue
                feed[field] = good_val
                recovered.append(f"feed.{field}")

            good_widgets = good_feed.get("widgets")
            gk = widgets_key(good_widgets)
            if (
                gk
                and gk != DEFAULT_WIDGETS_KEY
                and widgets_key(feed.get("widgets")) == DEFAULT_WIDGETS_KEY
            ):
                feed["widgets"] = good_widgets
                recovered.append("feed.widgets")

            if not recovered:
                continue

            prefs["feed"] = feed
            restored_any = True
            print(f"[{username}] restoring: {', '.join(recovered)}")
            print(
                json.dumps(
                    {"styles": styles, "preferences": prefs},
                    indent=2,
                    ensure_ascii=False,
                )
            )
            print()

            if APPLY:
                log_before = {
                    "preferences": user.preferences,
                    "styles": user.styles,
                }

                user.styles = styles
                user.preferences = prefs

                log_after = {
                    "preferences": user.preferences,
                    "styles": user.styles,
                }

                await create_log(
                    session,
                    constants.LOG_SETTINGS_CUSTOMIZATION,
                    user,
                    data={"before": log_before, "after": log_after},
                )

        if not restored_any:
            print("Nothing to restore.")
        elif APPLY:
            print("Committed.")
        else:
            print("DRY RUN — set APPLY = True to write these changes.")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_preferences())
