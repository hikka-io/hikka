from client_requests import request_anime_search
from fastapi import status


async def test_anime_list(client, aggregator_anime, aggregator_anime_info):
    # Make request to anime list
    response = await request_anime_search(client)

    assert response.status_code == status.HTTP_200_OK

    # Check pagination data
    assert response.json()["pagination"]["total"] == 16
    assert response.json()["pagination"]["pages"] == 2
    assert response.json()["pagination"]["page"] == 1

    # Check first anime slug
    assert (
        response.json()["list"][0]["slug"]
        == "fullmetal-alchemist-brotherhood-fc524a"
    )

    # Check last anime slug
    assert (
        response.json()["list"][11]["slug"]
        == "shingeki-no-kyojin-season-3-b22bb3"
    )


async def test_anime_no_meilisearch(client):
    # When Meilisearch is down search should throw query down error
    response = await request_anime_search(client, {"query": "test"})

    assert response.json()["code"] == "search:query_down"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_anime_pagination(
    client, aggregator_anime, aggregator_anime_info
):
    # Check second page of anime list
    response = await request_anime_search(client, page=2)

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["pagination"]["total"] == 16
    assert response.json()["pagination"]["pages"] == 2
    assert response.json()["pagination"]["page"] == 2

    # Check first anime on second page
    assert (
        response.json()["list"][0]["slug"]
        == "pia-carrot-e-youkoso-sayaka-no-koi-monogatari-227414"
    )


async def test_anime_pagination_size(
    client, aggregator_anime, aggregator_anime_info
):
    # Check second page of anime list
    response = await request_anime_search(client, page=1, size=2)
    assert response.status_code == status.HTTP_200_OK

    assert response.json()["pagination"]["total"] == 16
    assert response.json()["pagination"]["pages"] == 8
    assert response.json()["pagination"]["page"] == 1
