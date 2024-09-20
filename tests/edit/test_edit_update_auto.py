from client_requests import request_create_edit
from client_requests import request_update_edit
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
