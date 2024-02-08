from app.sync.history import generate_history
from sqlalchemy import select, func
from app.models import Log, History
from datetime import datetime
from app import constants
from uuid import uuid4


async def test_history_watch_update(test_session, create_test_user):
    user_id = create_test_user.id
    fake_anime_id = uuid4()

    test_logs = [
        {
            # User updates existing list record
            "created": datetime(2024, 2, 1, 3, 0, 0),
            "log_type": constants.LOG_WATCH_UPDATE,
            "target_id": fake_anime_id,
            "user_id": user_id,
            "data": {
                "before": {"status": constants.WATCH_PLANNED, "episodes": 0},
                "after": {"status": constants.WATCH_PLANNED, "episodes": 2},
            },
        },
    ]

    # Now store all logs to db
    test_session.add_all([Log(**log) for log in test_logs])
    await test_session.commit()

    # Count them (just in case)
    logs_count = await test_session.scalar(select(func.count(Log.id)))
    assert logs_count == 1

    # Generate history
    await generate_history(test_session)

    # Count history
    history_count = await test_session.scalar(select(func.count(History.id)))
    assert history_count == 1

    # And how get history entry
    history = await test_session.scalar(select(History))

    assert history.data == {
        "before": {"status": constants.WATCH_PLANNED, "episodes": 0},
        "after": {"status": constants.WATCH_PLANNED, "episodes": 2},
        "new_watch": False,
    }
