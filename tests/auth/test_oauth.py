from fastapi import status

from client_requests import (
    request_oauth_url,
    oauth_post,
)


async def test_provider(client):
    response = await request_oauth_url(client, "google")

    assert response.json()["url"] is not None
    assert response.status_code == status.HTTP_200_OK


async def test_invalid_provider(client):
    response = await request_oauth_url(client, "qwerty123")

    assert response.json()["code"] == "auth_invalid_provider"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_valid_oauth_signup(client, oauth_http):
    response = await oauth_post(client, "google", "code")

    assert response.json().get("secret") is not None
    assert response.status_code == status.HTTP_200_OK


# ToDo:
# Test invalid provider
# Test invalid code
# Test absent code
# Test both signup (no account exists) and login (account exists) (need a db lookup?)  # noqa: E501
# Test a case where a user with an email already exists
