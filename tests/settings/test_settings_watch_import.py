from client_requests import request_settings_import_watch
from app.models import AnimeWatch, User, Anime, Log
from client_requests import request_watch_add
from sqlalchemy import select, desc, func
from fastapi import status
from app import constants


async def test_settings_import_watch(
    client,
    create_test_user,
    aggregator_anime,
    aggregator_anime_info,
    get_test_token,
    test_session,
):
    # Add Bocchi to watch list
    response = await request_watch_add(
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

    # Create import request
    response = await request_settings_import_watch(
        client,
        get_test_token,
        {
            "overwrite": False,
            "anime": [
                {
                    "my_status": "Watching",
                    "series_animedb_id": 47917,
                    "my_watched_episodes": 9,
                    "my_comments": {},
                    "my_score": 10,
                },
                {
                    "my_status": "Completed",
                    "series_animedb_id": 16498,
                    "my_watched_episodes": 25,
                    "my_comments": {},
                    "my_score": 7,
                },
                {
                    "my_status": "Plan to Watch",
                    "series_animedb_id": 1,  # Bad mal_id
                    "my_watched_episodes": 0,
                    "my_comments": {},
                    "my_score": 0,
                },
            ],
        },
    )

    # Check status
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    # Check entries in database
    user = await test_session.scalar(
        select(User).filter(User.username == "testuser")
    )

    watch_count = await test_session.scalar(
        select(func.count(AnimeWatch.id)).filter(AnimeWatch.user == user)
    )

    assert watch_count == 2

    # Get Bocchi anime entry
    anime_bocchi = await test_session.scalar(
        select(Anime).filter(Anime.slug == "bocchi-the-rock-9e172d")
    )

    # Watch entry shouldn't be changed after import
    watch = await test_session.scalar(
        select(AnimeWatch).filter(
            AnimeWatch.anime == anime_bocchi, AnimeWatch.user == user
        )
    )

    assert watch is not None
    assert watch.status == constants.WATCH_WATCHING
    assert watch.duration == 230
    assert watch.episodes == 10
    assert watch.score == 8

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_SETTINGS_IMPORT
    assert log.user == create_test_user
    assert log.data["imported"] == 1
    assert log.data["overwrite"] is False
