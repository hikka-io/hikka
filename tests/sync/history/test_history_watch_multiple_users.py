from app.sync.history import generate_history
from sqlalchemy import select, func
from app.models import Log, History
from datetime import datetime
from app import constants
from uuid import uuid4


async def test_history_watch_multiple_users(
    test_session, create_test_user, create_dummy_user
):
    dummy_user_id = create_dummy_user.id
    user_id = create_test_user.id
    fake_anime_id = uuid4()

    test_logs = [
        {
            # Create log for test user
            "created": datetime(2024, 2, 1, 3, 0, 0),
            "log_type": constants.LOG_WATCH_UPDATE,
            "target_id": fake_anime_id,
            "user_id": user_id,
            "data": {
                "before": {"status": constants.WATCH_PLANNED, "episodes": 0},
                "after": {"status": constants.WATCH_PLANNED, "episodes": 2},
            },
        },
        {
            # Create log for dummy user
            "created": datetime(2024, 2, 1, 4, 0, 0),
            "log_type": constants.LOG_WATCH_CREATE,
            "target_id": fake_anime_id,
            "user_id": dummy_user_id,
            "data": {
                "before": {"status": None},
                "after": {"status": constants.WATCH_PLANNED},
            },
        },
    ]

    # Now store all logs to db
    test_session.add_all([Log(**log) for log in test_logs])
    await test_session.commit()

    # Count them (just in case)
    logs_count = await test_session.scalar(select(func.count(Log.id)))
    assert logs_count == 2

    # Generate history
    await generate_history(test_session)

    # Count history
    history_count = await test_session.scalar(select(func.count(History.id)))
    assert history_count == 2

    # And how get history entries
    history = await test_session.scalars(select(History))
    history = history.all()

    assert history[0].user_id == user_id
    assert history[0].data == {
        "before": {"status": constants.WATCH_PLANNED, "episodes": 0},
        "after": {"status": constants.WATCH_PLANNED, "episodes": 2},
        "new_watch": False,
    }

    assert history[1].user_id == dummy_user_id
    assert history[1].data == {
        "before": {"status": None},
        "after": {"status": constants.WATCH_PLANNED},
        "new_watch": True,
    }
