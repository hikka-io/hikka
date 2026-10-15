from client_requests import request_anime_search
from client_requests import request_watch_add
from fastapi import status


async def test_anime_list_exclude_watch(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    await request_watch_add(
        client,
        "shingeki-no-kyojin-0cf69a",
        get_test_token,
        {"status": "completed"},
    )

    await request_watch_add(
        client,
        "fullmetal-alchemist-brotherhood-fc524a",
        get_test_token,
        {"status": "planned"},
    )

    # Only completed anime is hidden
    response = await request_anime_search(
        client,
        {"exclude_watch_status": ["completed"]},
        size=20,
        token=get_test_token,
    )

    slugs = [anime["slug"] for anime in response.json()["list"]]

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 15
    assert "shingeki-no-kyojin-0cf69a" not in slugs
    assert "fullmetal-alchemist-brotherhood-fc524a" in slugs

    # Now both of them
    response = await request_anime_search(
        client,
        {"exclude_watch_status": ["completed", "planned"]},
        size=20,
        token=get_test_token,
    )

    slugs = [anime["slug"] for anime in response.json()["list"]]

    assert response.json()["pagination"]["total"] == 14
    assert "fullmetal-alchemist-brotherhood-fc524a" not in slugs

    # Anonymous user has no list so nothing is hidden
    response = await request_anime_search(
        client, {"exclude_watch_status": ["completed"]}, size=20
    )

    assert response.json()["pagination"]["total"] == 16


async def test_anime_search_exclude_watch(
    client,
    mock_meilisearch,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    await request_watch_add(
        client,
        "shingeki-no-kyojin-0cf69a",
        get_test_token,
        {"status": "completed"},
    )

    # Pretend Meilisearch returned anime from user list anyway
    mock_meilisearch.hits = [
        "0cf69ac6-9238-4e2f-9add-39294c1a0f11",
        "b22bb359-4545-45ce-92d3-df8646554128",
    ]
    mock_meilisearch.total = 2

    response = await request_anime_search(
        client,
        {"query": "kyojin", "exclude_watch_status": ["completed"]},
        token=get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK

    # Anime from user list is excluded in Meilisearch by id
    assert (
        'id NOT IN ["0cf69ac6-9238-4e2f-9add-39294c1a0f11"]'
        in mock_meilisearch.calls[0]["filter"]
    )

    # And database hides it as well
    assert [anime["slug"] for anime in response.json()["list"]] == [
        "shingeki-no-kyojin-season-3-b22bb3"
    ]

    # Without status filter Meilisearch gets no exclusion
    await request_anime_search(
        client, {"query": "kyojin"}, token=get_test_token
    )

    assert not any(
        "NOT IN" in str(entry) for entry in mock_meilisearch.calls[1]["filter"]
    )
