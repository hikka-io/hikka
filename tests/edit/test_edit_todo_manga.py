from client_requests import request_todo_manga_list
from fastapi import status


async def test_todo_manga_list(client, aggregator_manga):
    # None of the seeded manga have a synopsis, so all of them show up
    # as having issues by default
    response = await request_todo_manga_list(client)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 4
    assert len(response.json()["list"]) == 4


async def test_todo_manga_list_filter_by_mal_id(client, aggregator_manga):
    response = await request_todo_manga_list(client, {"mal_id": 2})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["slug"] == "berserk-fb9fbd"


async def test_todo_manga_list_filter_by_media_type(client, aggregator_manga):
    response = await request_todo_manga_list(client, {"media_type": "manhwa"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["mal_id"] == 125036


async def test_todo_manga_list_filter_by_issue(client, aggregator_manga):
    # Every seeded manga already has a title_en, so filtering for manga
    # missing one should return nothing
    response = await request_todo_manga_list(client, {"title_en": True})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0
    assert response.json()["list"] == []
