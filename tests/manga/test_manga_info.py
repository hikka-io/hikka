from client_requests import request_manga_info
from fastapi import status


async def test_manga_info(
    client,
    aggregator_genres,
    aggregator_companies,
    aggregator_manga,
    aggregator_manga_info,
):
    # Test for manga info endpoint
    response = await request_manga_info(client, "fullmetal-alchemist-7ef8d2")
    assert response.status_code == status.HTTP_200_OK

    # Make sure data is more or less what we expect to see
    assert response.json()["title_en"] == "Fullmetal Alchemist"

    assert response.json()["chapters"] == 116
    assert response.json()["volumes"] == 27
    assert response.json()["scored_by"] == 158333
    assert response.json()["score"] == 9.04

    assert len(response.json()["external"]) == 4
    assert len(response.json()["genres"]) == 6

    assert response.json()["translated_ua"] is True
    assert response.json()["stats"] == {
        "dropped": 6393,
        "on_hold": 16941,
        "planned": 62318,
        "reading": 49287,
        "score_1": 2686,
        "score_2": 155,
        "score_3": 141,
        "score_4": 275,
        "score_5": 892,
        "score_6": 2357,
        "score_7": 8653,
        "score_8": 24189,
        "score_9": 45644,
        "score_10": 73337,
        "completed": 160273,
    }
