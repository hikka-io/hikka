from app.sync.history import generate_history
from sqlalchemy import select, desc, func
from app.models import Log, History
from datetime import datetime
from typing import Iterator
from app import constants
from uuid import uuid4


async def test_history_read(test_session, create_test_user):
    user_id = create_test_user.id
    fake_manga_id = uuid4()

    test_logs = [
        {
            # First user adds title to his list as planned
            "created": datetime(2024, 2, 1, 0, 0, 0),
            "log_type": constants.LOG_READ_CREATE,
            "target_id": fake_manga_id,
            "user_id": user_id,
            "data": {
                "content_type": "manga",
                "before": {"status": None},
                "after": {"status": constants.READ_PLANNED},
            },
        },
        # After that user set as planned another manga
        {
            "created": datetime(2024, 2, 1, 0, 0, 1),
            "log_type": constants.LOG_READ_CREATE,
            "target_id": uuid4(),
            "user_id": user_id,
            "data": {
                "content_type": "manga",
                "before": {"status": None},
                "after": {"status": constants.READ_PLANNED},
            },
        },
        {
            # After that user reads 2 volumes and updates status
            "created": datetime(2024, 2, 1, 3, 0, 0),
            "log_type": constants.LOG_READ_UPDATE,
            "target_id": fake_manga_id,
            "user_id": user_id,
            "data": {
                "content_type": "manga",
                "before": {"status": constants.READ_PLANNED, "volumes": 0},
                "after": {"status": constants.READ_PLANNED, "volumes": 2},
            },
        },
        {
            # After 3 more volumes user drops manga and sets score
            "created": datetime(2024, 2, 1, 3, 40, 0),
            "log_type": constants.LOG_READ_UPDATE,
            "target_id": fake_manga_id,
            "user_id": user_id,
            "data": {
                "content_type": "manga",
                "before": {
                    "status": constants.READ_PLANNED,
                    "volumes": 2,
                    "score": 0,
                },
                "after": {
                    "status": constants.READ_DROPPED,
                    "volumes": 5,
                    "score": 5,
                },
            },
        },
        {
            # Couple hours went by and user caves in his binge
            "created": datetime(2024, 2, 1, 5, 10, 0),
            "log_type": constants.LOG_READ_UPDATE,
            "target_id": fake_manga_id,
            "user_id": user_id,
            "data": {
                "content_type": "manga",
                "before": {"status": constants.READ_DROPPED, "volumes": 5},
                "after": {"status": constants.READ_READING, "volumes": 9},
            },
        },
        {
            # Finally manga is finished and status changed
            "created": datetime(2024, 2, 2, 5, 50, 0),
            "log_type": constants.LOG_READ_UPDATE,
            "target_id": fake_manga_id,
            "user_id": user_id,
            "data": {
                "content_type": "manga",
                "before": {
                    "status": constants.READ_READING,
                    "volumes": 9,
                    "score": 5,
                },
                "after": {
                    "status": constants.READ_COMPLETED,
                    "volumes": 12,
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
    assert history_count == 4

    # And how get history entry
    result = await test_session.scalars(
        select(History).order_by(desc(History.created))
    )

    history: Iterator[History] = iter(result.all())

    record = next(history)
    assert len(record.used_logs) == 1
    assert record.data == {
        "before": {"volumes": 9, "score": 5, "status": "reading"},
        "after": {"volumes": 12, "score": 7, "status": "completed"},
        "new_read": False,
    }

    record = next(history)
    assert len(record.used_logs) == 3
    assert record.data == {
        "before": {"volumes": 0, "score": 0, "status": "planned"},
        "after": {"volumes": 9, "score": 5, "status": "reading"},
        "new_read": False,
    }

    record = next(history)
    assert len(record.used_logs) == 1
    assert record.data == {
        "after": {"status": "planned"},
        "before": {"status": None},
        "new_read": True,
    }

    record = next(history)
    assert len(record.used_logs) == 1
    assert record.data == {
        "after": {"status": "planned"},
        "before": {"status": None},
        "new_read": True,
    }
