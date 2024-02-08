from app.sync.history import generate_history
from sqlalchemy import select, func
from app.models import Log, History
from datetime import datetime
from app import constants
from uuid import uuid4


async def test_history_watch_delete(test_session, create_test_user):
    user_id = create_test_user.id
    fake_anime_id = uuid4()

    test_logs = [
        {
            # First user adds title to his list as planned
            "created": datetime(2024, 2, 1, 0, 0, 0),
            "log_type": constants.LOG_WATCH_CREATE,
            "target_id": fake_anime_id,
            "user_id": user_id,
            "data": {
                "before": {"status": None},
                "after": {"status": constants.WATCH_PLANNED},
            },
        },
        {
            # Then delete it :D
            "created": datetime(2024, 2, 2, 0, 0, 0),
            "log_type": constants.LOG_WATCH_DELETE,
            "target_id": fake_anime_id,
            "user_id": user_id,
            "data": {},
        },
        {
            # Now add again
            "created": datetime(2024, 2, 4, 0, 0, 0),
            "log_type": constants.LOG_WATCH_CREATE,
            "target_id": fake_anime_id,
            "user_id": user_id,
            "data": {
                "before": {"status": None, "episodes": None},
                "after": {"status": constants.WATCH_WATCHING, "episodes": 10},
            },
        },
        {
            # And now delete after threshold
            "created": datetime(2024, 2, 10, 1, 0, 0),
            "log_type": constants.LOG_WATCH_DELETE,
            "target_id": fake_anime_id,
            "user_id": user_id,
            "data": {},
        },
    ]

    # Now store all logs to db
    test_session.add_all([Log(**log) for log in test_logs])
    await test_session.commit()

    # Count them (just in case)
    logs_count = await test_session.scalar(select(func.count(Log.id)))
    assert logs_count == 4

    # Generate history
    await generate_history(test_session)

    # Count history
    history_count = await test_session.scalar(select(func.count(History.id)))
    assert history_count == 2

    # And how get history entries
    history = await test_session.scalars(select(History))
    history = history.all()

    assert history[0].history_type == constants.HISTORY_WATCH
    assert history[0].data == {
        "before": {"status": None, "episodes": None},
        "after": {"status": constants.WATCH_WATCHING, "episodes": 10},
        "new_watch": True,
    }

    assert history[1].history_type == constants.HISTORY_WATCH_DELETE
