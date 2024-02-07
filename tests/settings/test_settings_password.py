from client_requests import request_settings_password
from sqlalchemy import select, desc
from app.models import User, Log
from fastapi import status
from app import constants


async def test_settings_password(
    client, test_session, create_test_user, get_test_token
):
    # Get test user
    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    # Store old password hash
    old_hash = user.password_hash

    # Change password
    response = await request_settings_password(
        client, get_test_token, "new_password"
    )

    # Check response status
    assert response.status_code == status.HTTP_200_OK

    # Referesh user object
    await test_session.refresh(user)

    # And make sure password hash has changed
    assert user.password_hash != old_hash

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_SETTINGS_PASSWORD
    assert log.user == create_test_user
    assert log.data == {}
