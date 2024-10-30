from starlette import status

from app import constants

from tests.client_requests import (
    request_auth_token_request,
    request_auth_token_info,
    request_client_create,
    request_auth_token,
)


async def test_auth_thirdparty(client, test_token):
    name = "thirdparty-client"
    description = "Third-party client"
    endpoint = "hikka://auth/"

    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_200_OK

    client_info = response.json()

    client_reference = client_info["reference"]
    client_secret = client_info["secret"]

    response = await request_auth_token_request(
        client,
        test_token,
        client_reference,
        [constants.SCOPE_READ_USER_DETAILS],
    )

    assert response.status_code == status.HTTP_200_OK

    request_reference = response.json()["reference"]

    response = await request_auth_token(
        client, request_reference, client_secret
    )
    assert response.status_code == status.HTTP_200_OK

    thirdparty_token = response.json()["secret"]

    response = await request_auth_token_info(client, thirdparty_token)
    assert response.status_code == status.HTTP_200_OK

    token_info = response.json()

    assert token_info["client"]["reference"] == client_reference
