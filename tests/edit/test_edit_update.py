from client_requests import request_create_edit
from client_requests import request_update_edit
from client_requests import request_accept_edit
from app.models import Anime, Edit, Log
from sqlalchemy import select, desc
from fastapi import status
from app import constants
import asyncio


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

    # Simulate delay between create/update
    await asyncio.sleep(1)

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


async def test_edit_create_rate_limit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
    mock_utcnow,
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

    # Simulate delay between create/update
    await asyncio.sleep(1)

    update_edit_limit = 25

    for index in range(0, update_edit_limit + 1):
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

        # Make sure request prior to the rate limit is good
        if index == update_edit_limit - 1:
            assert response.status_code == status.HTTP_200_OK
            assert "code" not in response.json()

        # Check the rate limit
        if index == update_edit_limit:
            assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
            assert response.json()["code"] == "edit:rate_limit"


async def test_edit_update_parallel_accept(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_moderator,
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

    assert response.status_code == status.HTTP_200_OK
    edit_id = response.json()["edit_id"]

    # Author updates edit while moderator accepts it
    update_response, accept_response = await asyncio.gather(
        request_update_edit(
            client,
            get_test_token,
            edit_id,
            {
                "description": "Brief description 2",
                "after": {"title_en": "Bocchi The Rock! (Updated)"},
            },
        ),
        request_accept_edit(client, get_test_token, edit_id),
    )

    assert accept_response.status_code == status.HTTP_200_OK

    # Update either went through before accept or was rejected
    if update_response.status_code != status.HTTP_200_OK:
        assert update_response.status_code == status.HTTP_400_BAD_REQUEST
        assert update_response.json()["code"] == "edit:not_pending"

    edit = await test_session.scalar(
        select(Edit).filter(Edit.edit_id == edit_id)
    )

    anime = await test_session.scalar(
        select(Anime).filter(Anime.slug == "bocchi-the-rock-9e172d")
    )

    # Anime should get exactly what accepted edit has
    assert edit.status == constants.EDIT_ACCEPTED
    assert anime.title_en == edit.after["title_en"]
