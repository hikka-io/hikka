from client_requests import request_settings_import_watch
from app.models import AnimeWatch, User
from sqlalchemy import select, func
from fastapi import status


async def test_settings_import_watch(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
    test_session,
):
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
                },
                {
                    "my_status": "Plan to Watch",
                    "series_animedb_id": 1,  # Bad mal_id
                    "my_watched_episodes": 0,
                    "my_comments": {},
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

    assert watch_count == 1
