from client_requests import request_watch_random
from client_requests import request_watch_add
from fastapi import status


async def test_watch_random(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    anime_slugs = [
        "bocchi-the-rock-9e172d",
        "kimi-no-na-wa-945779",
        "kaguya-sama-wa-kokurasetai-ultra-romantic-fcd761",
    ]

    # Add bunch of titles in watch planned list
    for slug in anime_slugs:
        await request_watch_add(
            client, slug, get_test_token, {"status": "planned"}
        )

    # Make request for random anime in watch list
    response = await request_watch_random(client, "testuser", "planned")
    assert response.status_code == status.HTTP_200_OK

    # And check random anime slug
    assert response.json()["slug"] in anime_slugs
