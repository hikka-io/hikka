from client_requests import request_companies_search
from fastapi import status


async def test_companies_list(client, aggregator_companies):
    # Get companies list
    response = await request_companies_search(client)

    assert response.status_code == status.HTTP_200_OK

    # Make sure pagination data is ok
    assert response.json()["pagination"]["total"] == 39
    assert response.json()["pagination"]["pages"] == 3
    assert len(response.json()["list"]) == 15

    # Check first and last company slugs
    assert response.json()["list"][0]["slug"] == "mappa-360033"
    assert response.json()["list"][11]["slug"] == "square-enix-e62cc9"


async def test_companies_pagination(client, aggregator_companies):
    # Get companies list
    response = await request_companies_search(client, 2)

    assert response.status_code == status.HTTP_200_OK

    # Check data and length
    assert response.json()["pagination"]["total"] == 39
    assert response.json()["pagination"]["pages"] == 3
    assert response.json()["pagination"]["page"] == 2
    assert len(response.json()["list"]) == 15

    # Check first and last company slugs
    assert response.json()["list"][0]["slug"] == "majin-67e786"
    assert response.json()["list"][11]["slug"] == "movic-84c014"


async def test_companies_no_meilisearch(client, aggregator_companies):
    # When Meilisearch is down search should throw query down error
    response = await request_companies_search(client, 1, {"query": "test"})

    assert response.json()["code"] == "search:query_down"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
