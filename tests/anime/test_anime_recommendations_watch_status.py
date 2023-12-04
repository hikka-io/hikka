from client_requests import request_anime_recommendations, request_watch_add


async def test_anime_recommendations_watch_status(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    # Check recommendations for given anime
    response = await request_anime_recommendations(
        client, "shingeki-no-kyojin-0cf69a"
    )

    # User watch status should be empty
    assert response.json()["list"][0]["watch"] == []

    # Add FMA to watch list
    response = await request_watch_add(
        client,
        "fullmetal-alchemist-brotherhood-fc524a",
        get_test_token,
        {"status": "planned"},
    )

    # Check recommendations for SNK again
    response = await request_anime_recommendations(
        client, "shingeki-no-kyojin-0cf69a"
    )

    # User watch status should be empty (without auth)
    assert response.json()["list"][0]["watch"] == []

    # Now check recommendations with auth token
    response = await request_anime_recommendations(
        client, "shingeki-no-kyojin-0cf69a", get_test_token
    )

    # Watch status still should have 1 entry
    assert len(response.json()["list"][0]["watch"]) == 1
