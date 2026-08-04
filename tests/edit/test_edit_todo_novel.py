from client_requests import request_todo_novel_list
from fastapi import status


async def test_todo_novel_list(client, aggregator_novel):
    # None of the seeded novels have a synopsis, so all of them show up
    # as having issues by default
    response = await request_todo_novel_list(client)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2
    assert len(response.json()["list"]) == 2


async def test_todo_novel_list_filter_by_mal_id(client, aggregator_novel):
    response = await request_todo_novel_list(client, {"mal_id": 130826})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["slug"] == "tian-guan-cifu-7bb159"


async def test_todo_novel_list_filter_by_media_type(client, aggregator_novel):
    response = await request_todo_novel_list(
        client, {"media_type": "light_novel"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["mal_id"] == 60553


async def test_todo_novel_list_filter_by_issue(client, aggregator_novel):
    # Every seeded novel already has a title_en, so filtering for novels
    # missing one should return nothing
    response = await request_todo_novel_list(client, {"title_en": True})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0
    assert response.json()["list"] == []
