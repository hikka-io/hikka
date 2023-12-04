from client_requests import request_anime_franchise, request_watch_add


async def test_anime_franchise_watch_status(
    client,
    aggregator_anime,
    aggregator_anime_franchises,
    create_test_user,
    get_test_token,
):
    # Check franchise entries for SNK
    response = await request_anime_franchise(
        client, "shingeki-no-kyojin-0cf69a"
    )

    # User watch status should be empty
    assert response.json()["list"][0]["watch"] == []

    # Add final season of SNK to watch list
    await request_watch_add(
        client,
        "shingeki-no-kyojin-the-final-season-kanketsu-hen-833be1",
        get_test_token,
        {"status": "watching", "episodes": 1, "score": 8},
    )

    # Check franchise entries for SNK again
    response = await request_anime_franchise(
        client, "shingeki-no-kyojin-0cf69a"
    )

    # User watch status should be empty (without auth)
    assert response.json()["list"][0]["watch"] == []

    # Now check anime franchise with auth token
    response = await request_anime_franchise(
        client, "shingeki-no-kyojin-0cf69a", get_test_token
    )

    # Watch status still should have 1 entry
    assert len(response.json()["list"][0]["watch"]) == 1
