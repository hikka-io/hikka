from client_requests import request_companies_info
from fastapi import status


async def test_companies_info(client, aggregator_companies):
    # Get individual company info
    response = await request_companies_info(client, "mappa-360033")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "MAPPA"
    assert response.json()["slug"] == "mappa-360033"


async def test_companies_info_bad(client):
    # Try fetching non existing company
    response = await request_companies_info(client, "bad-company")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "company:not_found"
