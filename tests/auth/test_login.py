from client_requests import request_login
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_login(client, create_test_user, test_session):
    # Login
    response = await request_login(client, "user@mail.com", "password")
    assert response.status_code == status.HTTP_200_OK

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_LOGIN
    assert log.user == create_test_user
    assert log.data == {}


async def test_login_bad_password(client, create_test_user):
    # Login with bad password
    response = await request_login(client, "user@mail.com", "bad_password")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:invalid_password"


async def test_login_bad_captcha(client, create_test_user):
    # Login with bad captcha
    response = await request_login(
        client, "user@mail.com", "password", "bad_captcha"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["code"] == "captcha:invalid"
