from client_requests import request_create_edit
from client_requests import request_deny_edit
from fastapi import status
from app import constants


async def test_edit_deny(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_moderator,
    create_dummy_user,
    get_test_token,
    get_dummy_token,
    test_session,
):
    # Create edit for anime
    response = await request_create_edit(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        {
            "description": "Brief description",
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    # Check create status
    assert response.status_code == status.HTTP_200_OK

    # Deny edit
    response = await request_deny_edit(client, get_test_token, 1)

    # Make sure edit status and status code is correct
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == constants.EDIT_DENIED


async def test_edit_deny_bad_permission(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # Create edit for anime
    response = await request_create_edit(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        {
            "description": "Brief description",
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    # Check create status
    assert response.status_code == status.HTTP_200_OK

    # Try to deny edit
    response = await request_deny_edit(client, get_test_token, 1)

    # It should fail with permission denied
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"
