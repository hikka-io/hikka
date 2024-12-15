from client_requests import request_create_edit
from fastapi import status
from app import constants


async def test_edit_create_auto(
    client,
    aggregator_characters,
    aggregator_people,
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
            "after": {
                "title_en": "Bocchi The Rock!",
                "synonyms": ["bochchi"],  # This shoud be filtered out
            },
            "auto": True,
        },
    )

    # Check status and data
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == constants.EDIT_ACCEPTED


async def test_edit_create_auto_bad_permission(
    client,
    aggregator_characters,
    aggregator_people,
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
            "after": {
                "title_en": "Bocchi The Rock!",
                "synonyms": ["bochchi"],  # This shoud be filtered out
            },
            "auto": True,
        },
    )

    # Check status and data
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"
