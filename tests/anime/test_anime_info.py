from client_requests import request_anime_info
from fastapi import status


async def test_anime_info(
    client,
    aggregator_anime_genres,
    aggregator_companies,
    aggregator_anime,
    aggregator_anime_info,
):
    # Test for anime info endpoint
    response = await request_anime_info(client, "bocchi-the-rock-9e172d")

    assert response.status_code == status.HTTP_200_OK

    # Make sure data is more or less what we expect to see
    assert response.json()["title_en"] == "Bocchi the Rock!"
    assert response.json()["title_ua"] == "Самітниця-рокер!"
    assert response.json()["source"] == "4_koma_manga"
    assert response.json()["rating"] == "pg_13"

    assert response.json()["episodes_released"] == 12
    assert response.json()["episodes_total"] == 12
    assert response.json()["scored_by"] == 258904
    assert response.json()["score"] == 8.84

    assert len(response.json()["companies"]) == 3
    assert len(response.json()["external"]) == 11
    assert len(response.json()["videos"]) == 10
    assert len(response.json()["genres"]) == 2
    assert len(response.json()["ost"]) == 5

    assert response.json()["stats"] == {
        "completed": 284747,
        "dropped": 4858,
        "on_hold": 6363,
        "planned": 91586,
        "score_1": 1422,
        "score_10": 87424,
        "score_2": 278,
        "score_3": 295,
        "score_4": 669,
        "score_5": 1850,
        "score_6": 5203,
        "score_7": 20037,
        "score_8": 57034,
        "score_9": 84730,
        "watching": 53358,
    }


async def test_anime_info_bad(
    client,
    aggregator_anime,
):
    # Bad slug show throw error
    response = await request_anime_info(client, "bad-slug")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "anime:not_found"
