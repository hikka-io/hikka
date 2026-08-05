from client_requests import request_todo_anime_list
from fastapi import status


async def test_todo_anime_list(client, aggregator_anime):
    # None of the seeded anime have a synopsis, so all of them show up
    # as having issues by default
    response = await request_todo_anime_list(client)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 17
    assert len(response.json()["list"]) == 15


async def test_todo_anime_list_filter_by_mal_id(client, aggregator_anime):
    response = await request_todo_anime_list(client, {"mal_id": 47917})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["slug"] == "bocchi-the-rock-9e172d"


async def test_todo_anime_list_filter_by_media_type(client, aggregator_anime):
    response = await request_todo_anime_list(client, {"media_type": "movie"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert mal_ids == {32281, 216}


async def test_todo_anime_list_filter_by_issue(client, aggregator_anime):
    # Every seeded anime already has a title_original, so filtering for
    # anime missing one should return nothing
    response = await request_todo_anime_list(client, {"title_original": True})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0
    assert response.json()["list"] == []
