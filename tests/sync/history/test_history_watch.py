from app.sync.history import generate_history
from sqlalchemy import select, desc, func
from app.models import Log, History
from datetime import datetime
from app import constants
from uuid import uuid4


async def test_history_watch(test_session, create_test_user):
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
        # After that user set another title to his planned list
        {
            "created": datetime(2024, 2, 1, 0, 0, 1),
            "log_type": constants.LOG_WATCH_CREATE,
            "target_id": uuid4(),
            "user_id": user_id,
            "data": {
                "before": {"status": None},
                "after": {"status": constants.WATCH_PLANNED},
            },
        },
        {
            # After that user watches 2 episodes and updates status
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
            # After 3 more episodes user drops anime and sets score
            "created": datetime(2024, 2, 1, 3, 40, 0),
            "log_type": constants.LOG_WATCH_UPDATE,
            "target_id": fake_anime_id,
            "user_id": user_id,
            "data": {
                "before": {
                    "status": constants.WATCH_PLANNED,
                    "episodes": 2,
                    "score": 0,
                },
                "after": {
                    "status": constants.WATCH_DROPPED,
                    "episodes": 5,
                    "score": 5,
                },
            },
        },
        {
            # Couple hours went by and user caves in his binge
            "created": datetime(2024, 2, 1, 5, 10, 0),
            "log_type": constants.LOG_WATCH_UPDATE,
            "target_id": fake_anime_id,
            "user_id": user_id,
            "data": {
                "before": {"status": constants.WATCH_DROPPED, "episodes": 5},
                "after": {"status": constants.WATCH_WATCHING, "episodes": 9},
            },
        },
        {
            # Finally anime is finished and status changed
            # Everything under 6 hours (wow)
            "created": datetime(2024, 2, 1, 5, 50, 0),
            "log_type": constants.LOG_WATCH_UPDATE,
            "target_id": fake_anime_id,
            "user_id": user_id,
            "data": {
                "before": {
                    "status": constants.WATCH_WATCHING,
                    "episodes": 9,
                    "score": 5,
                },
                "after": {
                    "status": constants.WATCH_COMPLETED,
                    "episodes": 12,
                    "score": 7,
                },
            },
        },
    ]

    # Now store all logs to db
    test_session.add_all([Log(**log) for log in test_logs])
    await test_session.commit()

    # Count them (just in case)
    logs_count = await test_session.scalar(select(func.count(Log.id)))
    assert logs_count == len(test_logs)

    # Generate history
    await generate_history(test_session)

    # Count history
    history_count = await test_session.scalar(select(func.count(History.id)))
    assert history_count == 3

    # And how get history entry
    history = await test_session.scalars(
        select(History).order_by(desc(History.created))
    )
    history = history.all()

    assert len(history[0].used_logs) == 4
    assert history[0].data == {
        "after": {"episodes": 12, "score": 7, "status": "completed"},
        "before": {"episodes": 0, "score": 0, "status": "planned"},
        "new_watch": False,
    }

    assert len(history[1].used_logs) == 1
    assert history[1].data == {
        "after": {"status": "planned"},
        "before": {"status": None},
        "new_watch": True,
    }

    assert len(history[2].used_logs) == 1
    assert history[2].data == {
        "after": {"status": "planned"},
        "before": {"status": None},
        "new_watch": True,
    }
