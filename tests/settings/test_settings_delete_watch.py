from client_requests import request_settings_delete_watch
from client_requests import request_watch_add
from sqlalchemy import select, desc, func
from app.models import AnimeWatch, Log
from app import constants


async def test_settings_delete_watch(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    # Add Bocchi to watch list of test user
    await request_watch_add(
        client,
        "bocchi-the-rock-9e172d",
        get_test_token,
        {
            "status": "watching",
            "note": "Test",
            "episodes": 10,
            "score": 8,
        },
    )

    # Add Bocchi to watch list of dummy user
    await request_watch_add(
        client,
        "bocchi-the-rock-9e172d",
        get_dummy_token,
        {
            "status": "watching",
            "note": "Test",
            "episodes": 10,
            "score": 8,
        },
    )

    # Request watch list deletion for test user
    await request_settings_delete_watch(client, get_test_token)

    # Check database just in case
    watch_count_dummy = await test_session.scalar(
        select(func.count(AnimeWatch.id)).filter(
            AnimeWatch.user == create_dummy_user
        )
    )

    watch_count_test = await test_session.scalar(
        select(func.count(AnimeWatch.id)).filter(
            AnimeWatch.user == create_test_user
        )
    )

    assert watch_count_dummy == 1
    assert watch_count_test == 0

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_SETTINGS_WATCH_DELETE
    assert log.user == create_test_user
    assert log.data["watch_count"] == 1
