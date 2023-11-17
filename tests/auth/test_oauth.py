from fastapi import status

from client_requests import (
    request_oauth_post,
    request_oauth_url,
    request_me,
)


async def test_provider(client):
    response = await request_oauth_url(client, "google")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["url"] is not None


async def test_invalid_provider(client):
    response = await request_oauth_url(client, "qwerty123")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:invalid_provider"


async def test_valid_oauth_signup(client, oauth_http):
    response = await request_oauth_post(client, "google", "code")

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("secret") is not None


async def test_signup_invalid_provider(client, oauth_fail_http):
    response = await request_oauth_post(client, "qwerty123", "code")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:invalid_provider"


async def test_signup_invalid_code(client, oauth_fail_http):
    response = await request_oauth_post(client, "google", "invalidcode")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:invalid_code"


async def test_signup_absent_code(client, oauth_fail_http):
    response = await request_oauth_post(client, "google")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_valid_oauth_login(
    client, create_test_user_with_oauth, oauth_http
):
    response = await request_oauth_post(client, "google", "code")

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("secret") is not None


async def test_oauth_login_email_exists(
    client, create_test_user_oauth, oauth_http
):
    response = await request_oauth_post(client, "google", "code")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:email_exists"


async def test_valid_oauth_username(client, oauth_http):
    response = await request_oauth_post(client, "google", "code")

    # Check username created by oauth signup
    response = await request_me(client, response.json()["secret"])
    assert response.json()["username"] == "testuser"


async def test_valid_oauth_username_extra(client, create_test_user, oauth_http):
    response = await request_oauth_post(client, "google", "code")

    # Check username created by oauth signup
    response = await request_me(client, response.json()["secret"])
    assert response.json()["username"].startswith("testuser") is True
    assert len(response.json()["username"]) == 15
