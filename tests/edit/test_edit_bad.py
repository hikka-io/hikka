from client_requests import request_approve_edit
from client_requests import request_create_edit
from client_requests import request_deny_edit
from fastapi import status


async def test_edit_bad_permission_create(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    create_dummy_user_banned,
    get_test_token,
    get_dummy_token,
    test_session,
):
    # Create edit for anime
    response = await request_create_edit(
        client,
        get_dummy_token,
        "anime",
        "bocchi-the-rock-9e172d",
        {
            "description": "Brief description",
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    # Check status
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"


async def test_edit_bad_permission_approve(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    create_dummy_user_banned,
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

    # Check status
    assert response.status_code == status.HTTP_200_OK

    # Now make approve request
    response = await request_approve_edit(client, get_dummy_token, 1)

    # And hope it fails
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"


async def test_edit_bad_permission_deny(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    create_dummy_user_banned,
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

    # Check status
    assert response.status_code == status.HTTP_200_OK

    # Now make deny request
    response = await request_deny_edit(client, get_dummy_token, 1)

    # And it fails (right?)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"
