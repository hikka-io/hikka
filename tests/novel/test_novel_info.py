from client_requests import request_novel_info
from fastapi import status


async def test_novel_info(
    client,
    aggregator_genres,
    aggregator_companies,
    aggregator_novel,
    aggregator_novel_info,
):
    # Test for novel info endpoint
    response = await request_novel_info(
        client, "kono-subarashii-sekai-ni-shukufuku-wo-cc5525"
    )
    assert response.status_code == status.HTTP_200_OK

    # Make sure data is more or less what we expect to see
    assert (
        response.json()["title_en"]
        == "Konosuba: God's Blessing on This Wonderful World!"
    )

    assert response.json()["chapters"] == 127
    assert response.json()["volumes"] == 17
    assert response.json()["scored_by"] == 17510
    assert response.json()["score"] == 8.61

    # assert len(response.json()["authors"]) == 3
    assert len(response.json()["external"]) == 3
    assert len(response.json()["genres"]) == 5

    assert response.json()["translated_ua"] is False
    assert response.json()["stats"] == {
        "dropped": 1289,
        "on_hold": 3259,
        "planned": 22088,
        "reading": 16846,
        "score_1": 144,
        "score_2": 52,
        "score_3": 68,
        "score_4": 79,
        "score_5": 225,
        "score_6": 569,
        "score_7": 1611,
        "score_8": 3997,
        "score_9": 5297,
        "score_10": 5468,
        "completed": 10157,
    }
