from client_requests import request_accept_edit
from client_requests import request_create_edit
from client_requests import request_deny_edit
from sqlalchemy import select, desc, func
from fastapi import status
from app import constants
import asyncio

from app.models import (
    UserEditStats,
    Anime,
    Edit,
    Log,
)


async def test_edit_accept(
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

    # Check create status
    assert response.status_code == status.HTTP_200_OK

    # Accept edit
    response = await request_accept_edit(client, get_test_token, 18)

    # Make sure edit status and status code is correct
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == constants.EDIT_ACCEPTED

    # Get anime record from database
    anime = await test_session.scalar(
        select(Anime).filter(Anime.slug == "bocchi-the-rock-9e172d")
    )

    # And make sure title has been updated
    assert anime.title_en == "Bocchi The Rock!"
    assert "title_en" in anime.ignored_fields
    assert anime.needs_search_update is True

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_EDIT_ACCEPT
    assert log.user == create_test_user_moderator
    assert log.data == {}

    # Check top user stats
    stats = await test_session.scalar(select(UserEditStats))

    assert stats is not None
    assert stats.user == create_test_user_moderator
    assert stats.accepted == 1


async def test_edit_accept_bad_permission(
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

    # Try to accept edit
    response = await request_accept_edit(client, get_test_token, 18)

    # It should fail with permission denied
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"


async def test_edit_accept_bad_empty_edit(
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

    # Get edit record from database
    edit = await test_session.scalar(select(Edit).filter(Edit.edit_id == 18))

    # Set old title before accepting it
    edit.after = {"title_en": "Bocchi the Rock!"}

    test_session.add(edit)
    await test_session.commit()

    # Try to accept edit
    response = await request_accept_edit(client, get_test_token, 18)

    # It should fail with permission denied
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "edit:empty_edit"


async def test_edit_accept_bad_invalid_field(
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

    # Get edit record from database
    edit = await test_session.scalar(select(Edit).filter(Edit.edit_id == 18))

    # Set old title before accepting it
    edit.after = {"title_bad": "Bocchi the Rock!"}

    test_session.add(edit)
    await test_session.commit()

    # Try to accept edit
    response = await request_accept_edit(client, get_test_token, 18)

    # It should fail with permission denied
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "edit:invalid_field"


async def test_edit_accept_parallel(
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

    # Moderators accept and deny same edit at once
    responses = await asyncio.gather(
        request_accept_edit(client, get_test_token, edit_id),
        request_deny_edit(client, get_test_token, edit_id),
        request_accept_edit(client, get_test_token, edit_id),
    )

    # Only one of them should change edit status
    status_codes = [response.status_code for response in responses]
    assert status_codes.count(status.HTTP_200_OK) == 1

    for response in responses:
        if response.status_code == status.HTTP_200_OK:
            new_status = response.json()["status"]
            continue

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["code"] == "edit:not_pending"

    edit = await test_session.scalar(
        select(Edit).filter(Edit.edit_id == edit_id)
    )

    assert edit.status == new_status

    status_logs_count = await test_session.scalar(
        select(func.count(Log.id)).filter(
            Log.target_id == edit.id,
            Log.log_type.in_(
                [constants.LOG_EDIT_ACCEPT, constants.LOG_EDIT_DENY]
            ),
        )
    )

    assert status_logs_count == 1
