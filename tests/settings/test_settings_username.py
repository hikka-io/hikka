from client_requests import request_settings_username
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_settings_username(
    client, create_test_user, get_test_token, test_session
):
    # Change username for user
    response = await request_settings_username(
        client, get_test_token, "new_username"
    )

    # Now check if user username has been upated
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "new_username"

    # Change username again
    response = await request_settings_username(
        client, get_test_token, "new_username_2"
    )

    # It should hit rate limit
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "settings:username_cooldown"

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_SETTINGS_USERNAME
    assert log.user == create_test_user
    assert log.data["before"] == "testuser"
    assert log.data["after"] == "new_username"


async def test_settings_username_taken(
    client, create_dummy_user, create_test_user, get_test_token
):
    # Try setting used username
    response = await request_settings_username(client, get_test_token, "dummy")

    # It should throw an error
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "settings:username_taken"


async def test_settings_username_bad(client, create_test_user, get_test_token):
    # Now let's try setting up bad username
    response = await request_settings_username(
        client, get_test_token, "bad username"
    )

    # And it fails
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_settings_username_protected(
    client, create_test_user, get_test_token
):
    # Now let's try setting up protected username
    response = await request_settings_username(client, get_test_token, "hikka")

    # And it fails
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "settings:invalid_username"
