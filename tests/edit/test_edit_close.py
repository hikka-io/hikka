from client_requests import request_create_edit
from client_requests import request_close_edit
from app.models import ContentEdit
from sqlalchemy import select
from fastapi import status
from app import constants


async def test_edit_close(
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

    # Close edit
    response = await request_close_edit(client, get_test_token, 1)

    # Make sure edit status and status code is correct
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == constants.EDIT_CLOSED

    # Get edit record from database
    edit = await test_session.scalar(
        select(ContentEdit).filter(ContentEdit.edit_id == 1)
    )

    # Status should be closed
    assert edit.status == constants.EDIT_CLOSED


async def test_edit_close_bad_author(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
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

    # Close edit with bad author
    response = await request_close_edit(client, get_dummy_token, 1)

    # Make sure edit status and status code is correct
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "edit:not_author"


async def test_edit_close_bad_permission(
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

    # Check create status
    assert response.status_code == status.HTTP_200_OK

    # Close edit with account with no permissions
    response = await request_close_edit(client, get_dummy_token, 1)

    # And it fails :D
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"
