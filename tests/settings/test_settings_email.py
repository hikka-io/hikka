from client_requests import request_settings_email
from sqlalchemy import select
from app.models import User
from fastapi import status


async def test_settings_email(
    client, test_session, create_test_user, get_test_token
):
    # Get test user
    user = await test_session.scalar(
        select(User).filter(User.email == "user@mail.com")
    )

    # Change email for user
    response = await request_settings_email(
        client, get_test_token, "new@mail.com"
    )

    # Check if status is correct
    assert response.status_code == status.HTTP_200_OK

    # Now check if user email has been upated
    await test_session.refresh(user)
    assert user.email == "new@mail.com"
    assert user.email_confirmed is False

    # Try to change email again
    response = await request_settings_email(
        client, get_test_token, "not_so_new@mail.com"
    )

    # It should hit rate limit
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "settings:email_cooldown"
