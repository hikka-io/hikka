from fastapi import status

from client_requests import (
    request_oauth_url,
    oauth_post,
)

import re


async def test_provider(client):
    response = await request_oauth_url(client, "google")

    assert response.json()["url"] is not None
    assert response.status_code == status.HTTP_200_OK

    pattern = (
        r"^https:\/\/accounts\.google\.com\/o\/oauth2\/v2\/auth\?scope=[^&]"
        r"+&redirect_uri=[^&]"
    )

    assert re.match(pattern, response.json()["url"]) is not None


async def test_invalid_provider(client):
    response = await request_oauth_url(client, "qwerty123")

    assert response.json()["code"] == "auth_invalid_provider"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_valid_oauth_signup(client):
    response = await oauth_post(client, "google", "validoauthcode")

    assert response.json().get("secret") is not None
    assert response.status_code == status.HTTP_200_OK


# ToDo:
# Test invalid provider
# Test invalid code
# Test absent code
# Test both signup (no account exists) and login (account exists) (need a db lookup?)
# Test a case where a user with an email already exists
