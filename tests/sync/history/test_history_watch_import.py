from app.sync.history import generate_history
from sqlalchemy import select, func
from app.models import Log, History
from datetime import datetime
from app import constants


async def test_history_watch_import(test_session, create_test_user):
    user_id = create_test_user.id

    test_logs = [
        {
            "created": datetime(2024, 2, 1, 0, 0, 0),
            "log_type": constants.LOG_SETTINGS_IMPORT_WATCH,
            "target_id": None,
            "user_id": user_id,
            "data": {
                "imported": 10,
                "overwrite": True,
            },
        }
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

    assert history.history_type == constants.HISTORY_WATCH_IMPORT
    assert history.data == {
        "imported": 10,
        "overwrite": True,
    }
