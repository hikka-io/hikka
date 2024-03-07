from client_requests import (
    request_favourite_list,
    request_favourite_add,
    request_watch_add,
)


async def test_favourite_watch_status(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    # Add Bocchi to favourite
    await request_favourite_add(
        client, "bocchi-the-rock-9e172d", get_test_token
    )

    # Get user favourite list
    response = await request_favourite_list(client, "testuser")

    # User watch status should be empty
    assert response.json()["list"][0]["content"]["watch"] == []

    # Add Bocchi to watch list
    await request_watch_add(
        client,
        "bocchi-the-rock-9e172d",
        get_test_token,
        {
            "status": "watching",
            "episodes": 10,
            "score": 8,
        },
    )

    # Get user favourite list (without auth)
    response = await request_favourite_list(client, "testuser")

    # Watch status still should be empty
    assert response.json()["list"][0]["content"]["watch"] == []

    # Get user favourite list (with auth)
    response = await request_favourite_list(client, "testuser", get_test_token)

    # Watch status still should have 1 entry
    assert len(response.json()["list"][0]["content"]["watch"]) == 1
