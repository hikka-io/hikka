from client_requests import request_characters_search
from fastapi import status


async def test_characters_list(client, aggregator_characters):
    response = await request_characters_search(client)

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["pagination"]["total"] == 407
    assert response.json()["pagination"]["pages"] == 34
    assert len(response.json()["list"]) == 12

    assert response.json()["list"][0]["slug"] == "levi-565409"
    assert response.json()["list"][11]["slug"] == "armin-arlert-4fe343"


async def test_characters_no_meilisearch(client):
    response = await request_characters_search(client, {"query": "test"})

    assert response.json()["code"] == "search_query_down"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
