from fastapi import status

from client_requests import (
    request_oauth_url,
)


async def test_provider(client):
    response = await request_oauth_url(client, "google")

    assert response.json()["url"] is not None
    assert response.status_code == status.HTTP_200_OK


async def test_invalid_provider(client):
    response = await request_oauth_url(client, "qwerty123")

    assert response.json()["code"] == "auth_invalid_provider"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
