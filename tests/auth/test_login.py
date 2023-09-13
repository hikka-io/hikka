from client_requests import request_login
from fastapi import status


async def test_login(client, create_test_user):
    # Login
    response = await request_login(client, "user@mail.com", "password")
    assert response.status_code == status.HTTP_200_OK


async def test_login_bad_password(client, create_test_user):
    # Login with bad password
    response = await request_login(client, "user@mail.com", "bad_password")
    assert response.json()["code"] == "auth:invalid_password"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_login_not_activated(client, create_test_user_not_activated):
    # Login to not activated account
    response = await request_login(client, "user@mail.com", "password")
    assert response.json()["code"] == "auth:not_activated"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
