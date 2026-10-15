from client_requests import request_novel_search
from client_requests import request_read_add
from fastapi import status


async def test_novel_list_exclude_read(
    client,
    aggregator_novel,
    aggregator_novel_info,
    create_test_user,
    get_test_token,
):
    response = await request_novel_search(client, size=20)
    total = response.json()["pagination"]["total"]

    await request_read_add(
        client,
        "novel",
        "tian-guan-cifu-7bb159",
        get_test_token,
        {"status": "completed"},
    )

    # Completed novel is hidden
    response = await request_novel_search(
        client,
        {"exclude_read_status": ["completed"]},
        size=20,
        token=get_test_token,
    )

    slugs = [entry["slug"] for entry in response.json()["list"]]

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == total - 1
    assert "tian-guan-cifu-7bb159" not in slugs

    # Other statuses don't hide it
    response = await request_novel_search(
        client,
        {"exclude_read_status": ["planned"]},
        size=20,
        token=get_test_token,
    )

    assert response.json()["pagination"]["total"] == total


async def test_novel_search_exclude_read(
    client,
    mock_meilisearch,
    aggregator_novel,
    aggregator_novel_info,
    create_test_user,
    get_test_token,
):
    await request_read_add(
        client,
        "novel",
        "tian-guan-cifu-7bb159",
        get_test_token,
        {"status": "completed"},
    )

    # Pretend Meilisearch returned novel from user list anyway
    mock_meilisearch.hits = [
        "7bb1594b-9a84-4632-948d-594903e85676",
        "cc552518-5e42-43fa-a729-0f9a81db5767",
    ]
    mock_meilisearch.total = 2

    response = await request_novel_search(
        client,
        {"query": "novel", "exclude_read_status": ["completed"]},
        token=get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK

    # Novel from user list is excluded in Meilisearch by id
    assert (
        'id NOT IN ["7bb1594b-9a84-4632-948d-594903e85676"]'
        in mock_meilisearch.calls[0]["filter"]
    )

    # And database hides it as well
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["slug"] != "tian-guan-cifu-7bb159"
