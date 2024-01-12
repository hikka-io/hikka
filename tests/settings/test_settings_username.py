from client_requests import request_settings_username
from fastapi import status


async def test_settings_username(client, create_test_user, get_test_token):
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
