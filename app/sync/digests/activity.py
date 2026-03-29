from sqlalchemy import select, distinct, case, func
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timedelta
from app.database import sessionmanager
from app.utils import utcnow, chunkify
from collections import defaultdict
from app.models import Digest, Log
from app import constants


async def digest_activity():
    async with sessionmanager.session() as session:
        now = utcnow()
        max_date = now.date()
        min_date = max_date - timedelta(days=365)

        spam_types = [constants.LOG_FAVOURITE, constants.LOG_FOLLOW]

        activity = await session.execute(
            select(
                Log.user_id,
                func.date(Log.created).label("day"),
                (
                    func.count(
                        distinct(
                            case(
                                (Log.log_type.in_(spam_types), Log.target_id),
                            )
                        )
                    )
                    + func.count(
                        case(
                            (Log.log_type.not_in(spam_types), Log.id),
                        )
                    )
                ).label("actions"),
            )
            .filter(
                Log.log_type.in_(
                    [
                        constants.LOG_FAVOURITE,
                        constants.LOG_COMMENT_WRITE,
                        constants.LOG_FOLLOW,
                        constants.LOG_EDIT_CREATE,
                        constants.LOG_WATCH_CREATE,
                        constants.LOG_WATCH_UPDATE,
                        constants.LOG_READ_CREATE,
                        constants.LOG_READ_UPDATE,
                        constants.LOG_COLLECTION_CREATE,
                        constants.LOG_ARTICLE_CREATE,
                    ]
                ),
                Log.created >= min_date,
                Log.created <= max_date,
            )
            .group_by(Log.user_id, func.date(Log.created))
            .order_by(func.date(Log.created))
        )

        rows = activity.all()

        # Build dict of {user_id: {date: count}}
        user_activity = defaultdict(dict)
        all_dates = set()

        for user_id, day, count in rows:
            user_activity[user_id][day] = count
            all_dates.add(day)

        # Fill empty days with zeros
        result = {}

        for user_id, days in user_activity.items():
            entries = []
            current = min_date

            while current <= max_date:
                entries.append(
                    {
                        "timestamp": int(
                            datetime.combine(
                                current, datetime.min.time()
                            ).timestamp()
                        ),
                        "actions": days.get(current, 0),
                    }
                )

                current += timedelta(days=1)

            result[str(user_id)] = entries

        values = [
            {
                "name": constants.DIGEST_ACTIVITY,
                "user_id": user_id,
                "created": now,
                "updated": now,
                "data": data,
            }
            for user_id, data in result.items()
        ]

        for values_chunk in chunkify(values, 100):
            await session.execute(
                insert(Digest)
                .values(values_chunk)
                .on_conflict_do_update(
                    index_elements=["user_id", "name"],
                    set_={
                        "updated": insert(Digest).excluded.updated,
                        "data": insert(Digest).excluded.data,
                    },
                )
            )

        print(f"Updated activity digests for {len(result)} users")

        await session.commit()
