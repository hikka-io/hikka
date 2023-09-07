from client_requests import request_anime_search
from fastapi import status


async def test_anime_filter_studios(
    client,
    aggregator_companies,
    aggregator_anime,
    aggregator_anime_info,
):
    # Check for anime produced by CloverWorks
    response = await request_anime_search(
        client, {"studios": ["cloverworks-3c7a54"]}
    )

    assert len(response.json()["list"]) == 1

    # Check for anime produced by Doga Kobo
    response = await request_anime_search(
        client, {"studios": ["doga-kobo-5a9be5"]}
    )

    assert len(response.json()["list"]) == 1

    # Check for anime produced by both CloverWorks and Doga Kobo
    response = await request_anime_search(
        client, {"studios": ["cloverworks-3c7a54", "doga-kobo-5a9be5"]}
    )

    assert len(response.json()["list"]) == 2

    response = await request_anime_search(
        client, {"studios": ["unknown-studio"]}
    )

    assert response.json()["code"] == "anime_unknown_studio"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
