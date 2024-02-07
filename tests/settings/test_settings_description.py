from client_requests import request_settings_description
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_settings_description(
    client, create_test_user, get_test_token, test_session
):
    # Change description for user
    response = await request_settings_description(
        client, get_test_token, "Description"
    )

    # Now check if user description has been upated
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == "Description"

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_SETTINGS_DESCRIPTION
    assert log.user == create_test_user
    assert log.data["before"] is None
    assert log.data["after"] == "Description"


async def test_settings_bad_description(
    client, create_test_user, get_test_token
):
    # Change description for user with way to long string
    response = await request_settings_description(
        client,
        get_test_token,
        # 141 symbols with 140 limit
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",  # I scream, you scream, we all scream for ice cream
    )

    # This request should fail
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"
