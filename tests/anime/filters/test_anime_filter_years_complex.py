from client_requests import request_anime_search
from fastapi import status


async def test_anime_filter_years_complex(
    client, aggregator_anime, aggregator_anime_info
):
    response = await request_anime_search(
        client, {"years": [["winter", 2011], ["winter", 2013]]}
    )

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["slug"] == "steinsgate-f29797"
