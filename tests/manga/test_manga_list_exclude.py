from client_requests import request_manga_search
from client_requests import request_read_add
from fastapi import status


async def test_manga_list_exclude_read(
    client,
    aggregator_manga,
    aggregator_manga_info,
    create_test_user,
    get_test_token,
):
    response = await request_manga_search(client, size=20)
    total = response.json()["pagination"]["total"]

    await request_read_add(
        client,
        "manga",
        "berserk-fb9fbd",
        get_test_token,
        {"status": "completed"},
    )

    # Completed manga is hidden
    response = await request_manga_search(
        client,
        {"exclude_read_status": ["completed"]},
        size=20,
        token=get_test_token,
    )

    slugs = [entry["slug"] for entry in response.json()["list"]]

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == total - 1
    assert "berserk-fb9fbd" not in slugs

    # Other statuses don't hide it
    response = await request_manga_search(
        client,
        {"exclude_read_status": ["planned"]},
        size=20,
        token=get_test_token,
    )

    assert response.json()["pagination"]["total"] == total


async def test_manga_search_exclude_read(
    client,
    mock_meilisearch,
    aggregator_manga,
    aggregator_manga_info,
    create_test_user,
    get_test_token,
):
    await request_read_add(
        client,
        "manga",
        "berserk-fb9fbd",
        get_test_token,
        {"status": "completed"},
    )

    # Pretend Meilisearch returned manga from user list anyway
    mock_meilisearch.hits = [
        "fb9fbd44-76f6-4b22-9438-05d7e3a43c37",
        "7ef8d2cf-0565-4ddd-9498-7fae392a7421",
    ]
    mock_meilisearch.total = 2

    response = await request_manga_search(
        client,
        {"query": "manga", "exclude_read_status": ["completed"]},
        token=get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK

    # Manga from user list is excluded in Meilisearch by id
    assert (
        'id NOT IN ["fb9fbd44-76f6-4b22-9438-05d7e3a43c37"]'
        in mock_meilisearch.calls[0]["filter"]
    )

    # And database hides it as well
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["slug"] != "berserk-fb9fbd"
