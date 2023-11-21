from client_requests import request_settings_description
from fastapi import status


async def test_settings_description(client, create_test_user, get_test_token):
    # Change description for user
    response = await request_settings_description(
        client, get_test_token, "Description"
    )

    # Now check if user description has been upated
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == "Description"


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
