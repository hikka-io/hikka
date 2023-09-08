from client_requests import request_people_search
from fastapi import status


async def test_people_list(client, aggregator_people):
    # Get people list
    response = await request_people_search(client)

    assert response.status_code == status.HTTP_200_OK

    # Make sure pagination data is ok
    assert response.json()["pagination"]["total"] == 865
    assert response.json()["pagination"]["pages"] == 73
    assert len(response.json()["list"]) == 12

    # Check first and last people slugs
    assert response.json()["list"][0]["slug"] == "hiroshi-kamiya-124b1f"
    assert response.json()["list"][11]["slug"] == "makoto-shinkai-943611"


async def test_people_pagination(client, aggregator_people):
    # Get people list
    response = await request_people_search(client, {"page": 2})

    assert response.status_code == status.HTTP_200_OK

    # Make sure pagination data is ok
    assert response.json()["pagination"]["total"] == 865
    assert response.json()["pagination"]["pages"] == 73
    assert response.json()["pagination"]["page"] == 2
    assert len(response.json()["list"]) == 12

    from pprint import pprint

    pprint(response.json())

    # Check first and last people slugs
    assert response.json()["list"][0]["slug"] == "yuuichi-nakamura-ed1264"
    assert response.json()["list"][11]["slug"] == "nana-mizuki-cceb6a"


async def test_people_no_meilisearch(client):
    # When Meilisearch is down search should throw query down error
    response = await request_people_search(client, {"query": "test"})

    assert response.json()["code"] == "search_query_down"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
