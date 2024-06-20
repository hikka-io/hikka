from client_requests import request_manga_search
from fastapi import status


async def test_manga_list(
    client,
    aggregator_manga,
    aggregator_manga_info,
):
    # Make request to manga list
    response = await request_manga_search(client)

    assert response.status_code == status.HTTP_200_OK

    # Check pagination data
    assert response.json()["pagination"]["total"] == 4
    assert response.json()["pagination"]["pages"] == 1
    assert response.json()["pagination"]["page"] == 1

    # Check first manga slug
    assert response.json()["list"][0]["slug"] == "berserk-fb9fbd"

    # Check last manga slug
    assert response.json()["list"][3]["slug"] == "the-horizon-f9ebc0"
