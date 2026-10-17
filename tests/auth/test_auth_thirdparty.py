from starlette import status

from app import constants

from tests.client_requests import (
    request_auth_token_request,
    request_auth_token_info,
    request_favourite_add,
    request_client_create,
    request_watch_delete,
    request_auth_token,
    request_watch_add,
    request_watch,
)


async def test_auth_thirdparty(client, test_token, aggregator_anime):
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
        [
            constants.SCOPE_READ_USER_DETAILS,
            constants.SCOPE_UPDATE_WATCHLIST,
            constants.SCOPE_READ_WATCHLIST,
        ],
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

    # Watch dependencies call auth_required without scope only to get
    # the user so they must not block token which has the route scope
    response = await request_watch_add(
        client,
        "bocchi-the-rock-9e172d",
        thirdparty_token,
        {"status": "watching"},
    )
    assert response.status_code == status.HTTP_200_OK

    response = await request_watch(
        client, "bocchi-the-rock-9e172d", thirdparty_token
    )
    assert response.status_code == status.HTTP_200_OK

    response = await request_watch_delete(
        client, "bocchi-the-rock-9e172d", thirdparty_token
    )
    assert response.status_code == status.HTTP_200_OK

    # Endpoints which need scope token doesn't have are still denied
    response = await request_favourite_add(
        client, "anime", "bocchi-the-rock-9e172d", thirdparty_token
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"
