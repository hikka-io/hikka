from app.sync.activity import generate_activity
from sqlalchemy import select, desc, func
from app.models import Log, Activity
from datetime import datetime
from app import constants


async def test_activity(test_session, create_test_user, create_dummy_user):
    dummy_id = create_dummy_user.id
    user_id = create_test_user.id

    user_logs = [
        {
            "created": datetime(2024, 2, 1, 1, 0, 0),
            "log_type": constants.LOG_LOGIN,
            "user_id": user_id,
            "data": {},
        },
        {
            "created": datetime(2024, 2, 1, 2, 0, 0),
            "log_type": constants.LOG_LOGIN,
            "user_id": user_id,
            "data": {},
        },
        {
            "created": datetime(2024, 2, 1, 3, 0, 0),
            "log_type": constants.LOG_LOGIN,
            "user_id": user_id,
            "data": {},
        },
        {
            "created": datetime(2024, 2, 2, 1, 0, 0),
            "log_type": constants.LOG_LOGIN,
            "user_id": user_id,
            "data": {},
        },
        {
            "created": datetime(2024, 2, 4, 1, 0, 0),
            "log_type": constants.LOG_LOGIN,
            "user_id": user_id,
            "data": {},
        },
        {
            "created": datetime(2024, 2, 4, 10, 0, 0),
            "log_type": constants.LOG_LOGIN,
            "user_id": user_id,
            "data": {},
        },
    ]

    dummy_logs = [
        {
            "created": datetime(2024, 2, 2, 3, 0, 0),
            "log_type": constants.LOG_LOGIN,
            "user_id": dummy_id,
            "data": {},
        },
        {
            "created": datetime(2024, 2, 5, 6, 0, 0),
            "log_type": constants.LOG_LOGIN,
            "user_id": dummy_id,
            "data": {},
        },
        {
            "created": datetime(2024, 2, 7, 3, 0, 0),
            "log_type": constants.LOG_LOGIN,
            "user_id": dummy_id,
            "data": {},
        },
        {
            "created": datetime(2024, 2, 8, 3, 0, 0),
            "log_type": constants.LOG_LOGIN,
            "user_id": dummy_id,
            "data": {},
        },
    ]

    # Now let's add logs to db
    test_session.add_all([Log(**log) for log in user_logs])
    test_session.add_all([Log(**log) for log in dummy_logs])
    await test_session.commit()

    # Count user logs
    logs_count = await test_session.scalar(
        select(func.count(Log.id)).filter(Log.user == create_test_user)
    )
    assert logs_count == 6

    # Count dummy user logs
    logs_count = await test_session.scalar(
        select(func.count(Log.id)).filter(Log.user == create_dummy_user)
    )
    assert logs_count == 4

    # Now generate activity
    await generate_activity(test_session)

    # Calculate total activity
    activity_count = await test_session.scalar(select(func.count(Activity.id)))
    assert activity_count == 7

    # Calculate total activity of user
    activity_count = await test_session.scalar(
        select(func.count(Activity.id)).filter(
            Activity.user == create_test_user
        )
    )
    assert activity_count == 3

    # Calculate total activity of dummy
    activity_count = await test_session.scalar(
        select(func.count(Activity.id)).filter(
            Activity.user == create_dummy_user
        )
    )
    assert activity_count == 4

    # Get activity of user
    activity_user = await test_session.scalars(
        select(Activity)
        .filter(Activity.user == create_test_user)
        .order_by(desc(Activity.timestamp))
    )

    activity_user = activity_user.all()

    assert activity_user[0].timestamp == datetime(2024, 2, 4)
    assert activity_user[0].actions == 2

    assert activity_user[1].timestamp == datetime(2024, 2, 2)
    assert activity_user[1].actions == 1

    assert activity_user[2].timestamp == datetime(2024, 2, 1)
    assert activity_user[2].actions == 3

    # Get activity of dummy
    activity_dummy = await test_session.scalars(
        select(Activity)
        .filter(Activity.user == create_dummy_user)
        .order_by(desc(Activity.timestamp))
    )

    activity_dummy = activity_dummy.all()

    assert activity_dummy[0].timestamp == datetime(2024, 2, 8)
    assert activity_dummy[0].actions == 1

    assert activity_dummy[1].timestamp == datetime(2024, 2, 7)
    assert activity_dummy[1].actions == 1

    assert activity_dummy[2].timestamp == datetime(2024, 2, 5)
    assert activity_dummy[2].actions == 1

    assert activity_dummy[3].timestamp == datetime(2024, 2, 2)
    assert activity_dummy[3].actions == 1
