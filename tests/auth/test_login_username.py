from tests.client_requests import request_login_username
from sqlalchemy.ext.asyncio import AsyncSession
from async_asgi_testclient import TestClient
from sqlalchemy import select, desc
from app.models import Log, User
from fastapi import status
from app import constants


async def test_default(
    client: TestClient, create_test_user: User, test_session: AsyncSession
):
    # Login
    response = await request_login_username(
        client, create_test_user.username, "password"
    )
    assert response.status_code == status.HTTP_200_OK

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log is not None

    assert log.log_type == constants.LOG_LOGIN
    assert log.user == create_test_user
    assert log.data == {}


async def test_bad_password(client: TestClient, create_test_user: User):
    # Login with bad password
    response = await request_login_username(
        client, create_test_user.username, "bad_password"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:invalid_password"


async def test_bad_captcha(client: TestClient, create_test_user: User):
    # Login with bad captcha
    response = await request_login_username(
        client, create_test_user.username, "password", "bad_captcha"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["code"] == "captcha:invalid"
