from client_requests import request_anime_search
from fastapi import status


async def test_anime_filter_score(client, aggregator_anime):
    # Check for score filter between 9 and 10
    response = await request_anime_search(client, {"score": [9, 10]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 5

    min_score_anime = min(response.json()["list"], key=lambda x: x["score"])
    max_score_anime = max(response.json()["list"], key=lambda x: x["score"])

    assert min_score_anime["score"] >= 9
    assert max_score_anime["score"] <= 10

    # Check for score filter between 6 and 9
    response = await request_anime_search(client, {"score": [6, 9]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 10

    min_score_anime = min(response.json()["list"], key=lambda x: x["score"])
    max_score_anime = max(response.json()["list"], key=lambda x: x["score"])

    assert min_score_anime["score"] >= 6
    assert max_score_anime["score"] <= 9

    # Score should be in range of 0 to 10
    response = await request_anime_search(client, {"score": [-1, 5]})

    assert response.json()["code"] == "validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = await request_anime_search(client, {"score": [5, 11]})

    assert response.json()["code"] == "validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
