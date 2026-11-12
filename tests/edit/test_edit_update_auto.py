from client_requests import request_create_edit
from client_requests import request_update_edit
from client_requests import request_deny_edit
from app.models import Edit, Log
from sqlalchemy import select
from fastapi import status
from app import constants
import asyncio


async def test_edit_update_auto(
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
            "auto": True,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == constants.EDIT_ACCEPTED


async def test_edit_update_auto_parallel_deny(
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

    # Author updates edit with auto accept while moderator denies it
    update_response, deny_response = await asyncio.gather(
        request_update_edit(
            client,
            get_test_token,
            edit_id,
            {
                "description": "Brief description 2",
                "after": {"title_en": "Bocchi The Rock!"},
                "auto": True,
            },
        ),
        request_deny_edit(client, get_test_token, edit_id),
    )

    edit = await test_session.scalar(
        select(Edit).filter(Edit.edit_id == edit_id)
    )

    # Edit should end up either accepted or denied but not both
    status_logs = (
        await test_session.scalars(
            select(Log.log_type).filter(
                Log.target_id == edit.id,
                Log.log_type.in_(
                    [
                        constants.LOG_EDIT_UPDATE_ACCEPT_AUTO,
                        constants.LOG_EDIT_DENY,
                    ]
                ),
            )
        )
    ).all()

    assert len(status_logs) == 1

    if status_logs[0] == constants.LOG_EDIT_DENY:
        assert deny_response.status_code == status.HTTP_200_OK
        assert edit.status == constants.EDIT_DENIED

    else:
        assert deny_response.status_code == status.HTTP_400_BAD_REQUEST
        assert deny_response.json()["code"] == "edit:not_pending"
        assert edit.status == constants.EDIT_ACCEPTED
