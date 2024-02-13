from client_requests import request_watch_stats
from client_requests import request_watch_add
from fastapi import status


async def test_watch_stats(
    client,
    create_test_user,
    aggregator_anime,
    aggregator_anime_info,
    get_test_token,
):
    # User watch stats should be zero when we start
    response = await request_watch_stats(client, "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "duration": 0,
        "completed": 0,
        "watching": 0,
        "planned": 0,
        "on_hold": 0,
        "dropped": 0,
    }

    # Add anime to watch list
    await request_watch_add(
        client,
        "bocchi-the-rock-9e172d",
        get_test_token,
        {
            "status": "watching",
            "episodes": 1,
            "score": 8,
        },
    )

    # Add one more anime to watch list
    await request_watch_add(
        client,
        "oshi-no-ko-421060",
        get_test_token,
        {
            "status": "planned",
            "episodes": 0,
            "score": 0,
        },
    )

    # Now let's check again
    response = await request_watch_stats(client, "testuser")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "duration": 23,
        "completed": 0,
        "watching": 1,
        "planned": 1,
        "on_hold": 0,
        "dropped": 0,
    }
