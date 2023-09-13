from client_requests import request_anime_search
from fastapi import status


async def test_anime_filter_years(client, aggregator_anime):
    # Check year range between 2010 and 2018
    response = await request_anime_search(client, {"years": [2010, 2018]})

    assert response.status_code == status.HTTP_200_OK

    min_year_anime = min(response.json()["list"], key=lambda x: x["year"])
    max_year_anime = max(response.json()["list"], key=lambda x: x["year"])

    assert min_year_anime["year"] >= 2010
    assert max_year_anime["year"] <= 2018

    # Check year range between 2020 and 2023 (just in case)
    response = await request_anime_search(client, {"years": [2020, 2023]})

    assert response.status_code == status.HTTP_200_OK

    min_year_anime = min(response.json()["list"], key=lambda x: x["year"])
    max_year_anime = max(response.json()["list"], key=lambda x: x["year"])

    assert min_year_anime["year"] >= 2020
    assert max_year_anime["year"] <= 2023

    # Check for bad year placement
    response = await request_anime_search(client, {"years": [2023, 2020]})

    assert response.json()["code"] == "system:validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Check for negative value
    response = await request_anime_search(client, {"years": [None, -1]})

    assert response.json()["code"] == "system:validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
