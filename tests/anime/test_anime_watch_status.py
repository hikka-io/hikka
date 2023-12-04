from client_requests import (
    request_anime_search,
    request_watch_add,
)


async def test_anime_watch_status(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    # Get anime catalog
    response = await request_anime_search(client)

    # User watch status should be empty
    assert response.json()["list"][0]["watch"] == []

    # Add FMA to watch list
    response = await request_watch_add(
        client,
        "fullmetal-alchemist-brotherhood-fc524a",
        get_test_token,
        {"status": "planned"},
    )

    # Get anime catalog again (without auth)
    response = await request_anime_search(client)

    # User watch status should be empty
    assert response.json()["list"][0]["watch"] == []

    # And one last time with auth token now
    response = await request_anime_search(client, token=get_test_token)

    # Watch status still should have 1 entry
    assert len(response.json()["list"][0]["watch"]) == 1
