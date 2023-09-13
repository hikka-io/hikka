from fastapi import status

from client_requests import (
    request_oauth_url,
    request_oauth_post,
)


async def test_provider(client):
    response = await request_oauth_url(client, "google")

    assert response.json()["url"] is not None
    assert response.status_code == status.HTTP_200_OK


async def test_invalid_provider(client):
    response = await request_oauth_url(client, "qwerty123")

    assert response.json()["code"] == "auth:invalid_provider"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_valid_oauth_signup(client, oauth_http):
    response = await request_oauth_post(client, "google", "code")

    assert response.json().get("secret") is not None
    assert response.status_code == status.HTTP_200_OK


async def test_signup_invalid_provider(client, oauth_fail_http):
    response = await request_oauth_post(client, "qwerty123", "code")

    assert response.json().get("secret") is None
    assert response.json()["code"] == "auth:invalid_provider"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_signup_invalid_code(client, oauth_fail_http):
    response = await request_oauth_post(client, "google", "invalidcode")

    assert response.json().get("secret") is None
    assert response.json()["code"] == "auth:invalid_code"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_signup_absent_code(client, oauth_fail_http):
    response = await request_oauth_post(client, "google")

    assert response.json().get("secret") is None
    assert response.json()["code"] == "system:validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_valid_oauth_login(
    client, create_test_user_with_oauth, oauth_http
):
    response = await request_oauth_post(client, "google", "code")

    assert response.json().get("secret") is not None
    assert response.status_code == status.HTTP_200_OK


async def test_oauth_login_email_exists(client, create_test_user, oauth_http):
    response = await request_oauth_post(client, "google", "code")

    assert response.json().get("secret") is None
    assert response.json()["code"] == "auth:email_exists"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
