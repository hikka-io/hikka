from client_requests import request_characters_search
from fastapi import status


async def test_characters_list(client, aggregator_characters):
    # Get characters list
    response = await request_characters_search(client)

    assert response.status_code == status.HTTP_200_OK

    # Make sure pagination data is ok
    assert response.json()["pagination"]["total"] == 419
    assert response.json()["pagination"]["pages"] == 28
    assert len(response.json()["list"]) == 15

    # Check first and last character slugs
    assert response.json()["list"][0]["slug"] == "levi-565409"
    assert response.json()["list"][11]["slug"] == "armin-arlert-4fe343"


async def test_characters_pagination(client, aggregator_characters):
    # Get characters list
    response = await request_characters_search(client, {"page": 2})

    assert response.status_code == status.HTTP_200_OK

    # Make sure pagination data is ok
    assert response.json()["pagination"]["total"] == 419
    assert response.json()["pagination"]["pages"] == 28
    assert response.json()["pagination"]["page"] == 2
    assert len(response.json()["list"]) == 15

    # Check first and last character slugs
    assert response.json()["list"][0]["slug"] == "gabi-braun-41f94a"
    assert response.json()["list"][11]["slug"] == "ai-hoshino-d7d467"


async def test_characters_no_meilisearch(client):
    # When Meilisearch is down search should throw query down error
    response = await request_characters_search(client, {"query": "test"})

    assert response.json()["code"] == "search:query_down"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
