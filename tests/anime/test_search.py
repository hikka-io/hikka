from client_requests import request_anime_search
from fastapi import status


async def test_anime_list(client, aggregator_anime):
    response = await request_anime_search(client)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 5

    # Check first anime slug
    assert (
        response.json()["list"][0]["slug"]
        == "fullmetal-alchemist-brotherhood-fc524a"
    )

    # Check last anime slug
    assert (
        response.json()["list"][4]["slug"]
        == "kaguya-sama-wa-kokurasetai-tensai-tachi-no-renai-zunousen-a3ac07"
    )


async def test_anime_no_meilisearch(client, aggregator_anime):
    response = await request_anime_search(client, {"query": "test"})

    assert response.json()["code"] == "search_query_down"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_anime_filters(client, aggregator_anime):
    pass


async def test_anime_pagination(client, aggregator_anime):
    pass
