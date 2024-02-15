from client_requests import request_create_edit
from client_requests import request_update_edit
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_edit_update(
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

    # Check status
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["created"] == response.json()["updated"]

    # Update created edit
    response = await request_update_edit(
        client,
        get_test_token,
        18,
        {
            "description": "Brief description 2",
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == "Brief description 2"
    assert response.json()["created"] != response.json()["updated"]

    # Update edit empty
    response = await request_update_edit(
        client,
        get_test_token,
        18,
        {
            "description": "Brief description for empty edit",
            "after": {"title_en": "Bocchi the Rock!"},
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "edit:empty_edit"

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_EDIT_UPDATE
    assert log.user == create_test_user

    assert log.data["old_edit"] == {
        "description": "Brief description",
        "after": {"title_en": "Bocchi The Rock!"},
    }

    assert log.data["updated_edit"] == {
        "description": "Brief description 2",
        "after": {"title_en": "Bocchi The Rock!"},
    }


async def test_edit_update_bad_author(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    create_dummy_user,
    get_dummy_token,
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

    # Check status
    assert response.status_code == status.HTTP_200_OK

    # Update edit by dummy user
    response = await request_update_edit(
        client,
        get_dummy_token,
        18,
        {
            "description": "Brief description 2",
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"


async def test_edit_update_moderator(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_moderator,
    create_dummy_user,
    get_dummy_token,
    get_test_token,
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
    assert response.status_code == status.HTTP_200_OK

    # Update edit by test user moderator
    response = await request_update_edit(
        client,
        get_test_token,
        18,
        {
            "description": "Brief description 2",
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    assert response.status_code == status.HTTP_200_OK
