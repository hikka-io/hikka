from app.models import Digest
from app.utils import utcnow
from starlette import status
from app import constants

from tests.client_requests import (
    request_settings_ignored_notifications,
    request_settings_customization,
    request_digest_privacy_info,
    request_auth_token_request,
    request_auth_token_info,
    request_digest_privacy,
    request_favourite_add,
    request_client_create,
    request_follow_check,
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
    assert response.json()["redirect_url"] == (
        f"hikka://auth/?reference={request_reference}"
    )

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


async def create_thirdparty_client(client, test_token):
    response = await request_client_create(
        client,
        test_token,
        "thirdparty-client",
        "Third-party client",
        "hikka://auth/",
    )

    assert response.status_code == status.HTTP_200_OK

    return response.json()


async def get_thirdparty_token(client, test_token, client_info, scope):
    response = await request_auth_token_request(
        client, test_token, client_info["reference"], scope
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_auth_token(
        client, response.json()["reference"], client_info["secret"]
    )

    assert response.status_code == status.HTTP_200_OK

    return response.json()["secret"]


async def test_thirdparty_follow_check(client, test_token, create_dummy_user):
    client_info = await create_thirdparty_client(client, test_token)

    # Follow status belongs to follow scopes
    token = await get_thirdparty_token(
        client, test_token, client_info, [constants.SCOPE_READ_FOLLOW]
    )

    response = await request_follow_check(client, token, "dummy")
    assert response.status_code == status.HTTP_200_OK

    # Favourite scope has nothing to do with it
    token = await get_thirdparty_token(
        client, test_token, client_info, [constants.SCOPE_READ_FAVOURITE]
    )

    response = await request_follow_check(client, token, "dummy")
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_thirdparty_digest_privacy(
    client, test_user, test_token, test_session
):
    now = utcnow()

    test_session.add(
        Digest(
            user_id=test_user.id,
            data={},
            created=now,
            updated=now,
            name="test",
        )
    )

    await test_session.commit()

    client_info = await create_thirdparty_client(client, test_token)

    # Upload scope has nothing to do with digests
    token = await get_thirdparty_token(
        client, test_token, client_info, [constants.SCOPE_UPLOAD]
    )

    response = await request_digest_privacy_info(client, "test", token)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await request_digest_privacy(client, "test", True, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Reading privacy is part of user details
    token = await get_thirdparty_token(
        client, test_token, client_info, [constants.SCOPE_READ_USER_DETAILS]
    )

    response = await request_digest_privacy_info(client, "test", token)
    assert response.status_code == status.HTTP_200_OK

    response = await request_digest_privacy(client, "test", True, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # And changing it has its own scope
    token = await get_thirdparty_token(
        client, test_token, client_info, [constants.SCOPE_UPDATE_USER_DIGESTS]
    )

    response = await request_digest_privacy(client, "test", True, token)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["private"] is True


async def test_thirdparty_customization(client, test_token):
    client_info = await create_thirdparty_client(client, test_token)

    # Customization scope used to be rejected on token request
    token = await get_thirdparty_token(
        client,
        test_token,
        client_info,
        [constants.SCOPE_UPDATE_USER_CUSTOMIZATION],
    )

    response = await request_settings_customization(
        client,
        token,
        {
            "preferences": {
                "title_language": None,
                "name_language": None,
                "effects": None,
            },
            "styles": {
                "overrides": {"light": None, "dark": None},
                "brand": None,
                "radius": None,
            },
        },
    )

    assert response.status_code == status.HTTP_200_OK


async def test_thirdparty_ignored_notifications(client, test_token):
    client_info = await create_thirdparty_client(client, test_token)

    # Own scope is enough without the rest of user details
    token = await get_thirdparty_token(
        client,
        test_token,
        client_info,
        [constants.SCOPE_UPDATE_USER_NOTIFICATIONS],
    )

    response = await request_settings_ignored_notifications(client, token, [])
    assert response.status_code == status.HTTP_200_OK

    # Other user details scopes don't give access to it
    token = await get_thirdparty_token(
        client, test_token, client_info, [constants.SCOPE_UPDATE_USER_USERNAME]
    )

    response = await request_settings_ignored_notifications(client, token, [])
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Whole user details group still includes it
    token = await get_thirdparty_token(
        client, test_token, client_info, [constants.SCOPE_UPDATE_USER_DETAILS]
    )

    response = await request_settings_ignored_notifications(client, token, [])
    assert response.status_code == status.HTTP_200_OK
