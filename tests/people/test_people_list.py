from client_requests import request_people_search
from fastapi import status


async def test_people_list(client, aggregator_people):
    # Get people list
    response = await request_people_search(client)

    assert response.status_code == status.HTTP_200_OK

    # Make sure pagination data is ok
    assert response.json()["pagination"]["total"] == 865
    assert response.json()["pagination"]["pages"] == 58
    assert len(response.json()["list"]) == 15

    # Check first and last people slugs
    assert response.json()["list"][0]["slug"] == "hiroshi-kamiya-124b1f"
    assert response.json()["list"][11]["slug"] == "makoto-shinkai-943611"


async def test_people_pagination(client, aggregator_people):
    # Get people list
    response = await request_people_search(client, 2)

    assert response.status_code == status.HTTP_200_OK

    # Make sure pagination data is ok
    assert response.json()["pagination"]["total"] == 865
    assert response.json()["pagination"]["pages"] == 58
    assert response.json()["pagination"]["page"] == 2
    assert len(response.json()["list"]) == 15

    # Check first and last people slugs
    assert response.json()["list"][0]["slug"] == "natsuki-hanae-0b8b74"
    assert response.json()["list"][11]["slug"] == "hiromu-arakawa-ea706d"


async def test_people_no_meilisearch(client):
    # When Meilisearch is down search should throw query down error
    response = await request_people_search(client, 1, {"query": "test"})

    assert response.json()["code"] == "search:query_down"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
