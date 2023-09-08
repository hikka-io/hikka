from client_requests import request_companies_anime
from fastapi import status


async def test_companies_anime(
    client,
    aggregator_companies,
    aggregator_anime,
    aggregator_anime_info,
):
    # Get anime produced by MAPPA
    response = await request_companies_anime(client, "mappa-360033")

    assert response.status_code == status.HTTP_200_OK

    from pprint import pprint

    pprint(response.json())

    # Check slugs
    assert response.json()["list"][0]["type"] == "studio"
    assert (
        response.json()["list"][0]["anime"]["slug"]
        == "shingeki-no-kyojin-the-final-season-kanketsu-hen-833be1"
    )

    assert response.json()["list"][2]["type"] == "studio"
    assert (
        response.json()["list"][2]["anime"]["slug"]
        == "shingeki-no-kyojin-the-final-season-part-2-8d3fc3"
    )
