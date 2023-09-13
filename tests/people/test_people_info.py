from client_requests import request_people_info
from fastapi import status


async def test_people_info(client, aggregator_people):
    # Get individual person info
    response = await request_people_info(client, "makoto-shinkai-943611")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name_en"] == "Makoto Shinkai"
    assert response.json()["slug"] == "makoto-shinkai-943611"


async def test_people_info_bad(client):
    # Try fetching non existing person
    response = await request_people_info(client, "bad-person")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "person:not_found"
