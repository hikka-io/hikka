from app.sync.digests.activity import generate_activity
from datetime import datetime, timedelta
from sqlalchemy import select, func
from app.models import Digest, Log
from app.utils import utcnow
from app import constants
from uuid import uuid4


async def test_activity(test_session, create_test_user):
    user_id = create_test_user.id

    now = utcnow()
    spam_target_id = uuid4()
    today = now.date()

    user_logs = [
        # Tracked actions
        {
            "created": now - timedelta(days=2, hours=1),
            "log_type": constants.LOG_COMMENT_WRITE,
            "user_id": user_id,
            "data": {},
        },
        {
            "created": now - timedelta(days=2, hours=2),
            "log_type": constants.LOG_EDIT_CREATE,
            "user_id": user_id,
            "data": {},
        },
        {
            "created": now - timedelta(days=1),
            "log_type": constants.LOG_WATCH_CREATE,
            "user_id": user_id,
            "data": {},
        },
        # Spam actions, we count them as one
        {
            "created": now - timedelta(days=3, hours=1),
            "log_type": constants.LOG_FAVOURITE,
            "target_id": spam_target_id,
            "user_id": user_id,
            "data": {},
        },
        {
            "created": now - timedelta(days=3, hours=2),
            "log_type": constants.LOG_FAVOURITE,
            "target_id": spam_target_id,
            "user_id": user_id,
            "data": {},
        },
        {
            "created": now - timedelta(days=3, hours=3),
            "log_type": constants.LOG_FAVOURITE,
            "target_id": spam_target_id,
            "user_id": user_id,
            "data": {},
        },
    ]

    test_session.add_all([Log(**log) for log in user_logs])
    await test_session.commit()

    await generate_activity(test_session)

    digest = await test_session.scalar(
        select(Digest).filter(
            Digest.user_id == user_id,
            Digest.name == constants.DIGEST_ACTIVITY,
        )
    )

    assert digest is not None

    data = digest.data
    assert len(data) == 365

    activity = {entry["timestamp"]: entry["actions"] for entry in data}

    day_minus_1 = int(
        datetime.combine(
            today - timedelta(days=1), datetime.min.time()
        ).timestamp()
    )

    day_minus_2 = int(
        datetime.combine(
            today - timedelta(days=2), datetime.min.time()
        ).timestamp()
    )

    day_minus_3 = int(
        datetime.combine(
            today - timedelta(days=3), datetime.min.time()
        ).timestamp()
    )

    assert activity[day_minus_1] == 1  # 1 watch
    assert activity[day_minus_2] == 2  # 1 comment + 1 edit
    assert activity[day_minus_3] == 1  # 3 favourites on same target = 1

    # Check days with no activity for zeros
    day_minus_10 = int(
        datetime.combine(
            today - timedelta(days=10), datetime.min.time()
        ).timestamp()
    )

    assert activity[day_minus_10] == 0

    # There should be no diplicates
    await generate_activity(test_session)

    digest_count = await test_session.scalar(
        select(func.count(Digest.id)).filter(
            Digest.name == constants.DIGEST_ACTIVITY,
        )
    )
    assert digest_count == 1
