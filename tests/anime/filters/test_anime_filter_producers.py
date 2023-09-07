from client_requests import request_anime_search
from fastapi import status


async def test_anime_filter_producers(
    client,
    aggregator_companies,
    aggregator_anime,
    aggregator_anime_info,
):
    # Check for anime produced by Aniplex
    response = await request_anime_search(
        client, {"producers": ["aniplex-332844"]}
    )

    assert len(response.json()["list"]) == 5

    # Check for anime produced by CyberAgent
    response = await request_anime_search(
        client, {"producers": ["cyberagent-4efc9f"]}
    )

    assert len(response.json()["list"]) == 1

    # Check for anime produced by both Aniplex and CyberAgent
    response = await request_anime_search(
        client, {"producers": ["aniplex-332844", "cyberagent-4efc9f"]}
    )

    assert len(response.json()["list"]) == 6

    response = await request_anime_search(
        client, {"producers": ["unknown-producer"]}
    )

    assert response.json()["code"] == "anime_unknown_producer"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
