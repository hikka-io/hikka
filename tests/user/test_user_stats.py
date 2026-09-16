from app.sync.digests.user_stats import generate_user_stats
from client_requests import request_favourite_add
from client_requests import request_user_stats
from fastapi import status


async def test_user_stats_favourites(
    client,
    create_test_user,
    aggregator_anime,
    aggregator_people,
    get_test_token,
    test_session,
):
    # Add both anime and person to favourite
    await request_favourite_add(
        client, "anime", "bocchi-the-rock-9e172d", get_test_token
    )

    await request_favourite_add(
        client, "person", "makoto-shinkai-943611", get_test_token
    )

    # Build user stats digest out of favourite logs
    await generate_user_stats(test_session)

    response = await request_user_stats(client, "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["favourites_count"]["anime"] == 1
    assert response.json()["favourites_count"]["person"] == 1
    assert response.json()["favourites_count"]["character"] == 0
