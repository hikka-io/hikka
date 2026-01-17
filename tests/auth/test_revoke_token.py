from starlette import status

from tests.client_requests import (
    request_auth_token_info,
    request_revoke_token,
)


async def test_revoke_token(client, test_token):
    response = await request_auth_token_info(client, test_token)
    assert response.status_code == status.HTTP_200_OK

    token_reference = response.json()["reference"]

    response = await request_revoke_token(client, test_token, token_reference)
    assert response.status_code == status.HTTP_200_OK

    response = await request_auth_token_info(client, test_token)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_revoke_thirdparty_token(
    client, test_token, test_thirdparty_client, test_thirdparty_token
):

    response = await request_auth_token_info(client, test_thirdparty_token)
    assert response.status_code == status.HTTP_200_OK

    token_info = response.json()

    assert token_info["client"]["reference"] == test_thirdparty_client.reference

    response = await request_revoke_token(
        client, test_thirdparty_token, token_info["reference"]
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"

    response = await request_revoke_token(
        client, test_token, token_info["reference"]
    )
    assert response.status_code == status.HTTP_200_OK

    response = await request_auth_token_info(client, test_thirdparty_token)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["code"] == "auth:invalid_token"
