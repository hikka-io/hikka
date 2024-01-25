from client_requests import request_create_edit
from sqlalchemy import select
from fastapi import status
from app import constants

from app.models import (
    PersonEdit,
    AnimeEdit,
    Edit,
)


async def test_edit_create(
    client,
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
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    # Check status and data
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json()["created"], int)

    assert response.json()["after"]["title_en"] == "Bocchi The Rock!"
    assert response.json()["description"] == "Brief description"
    assert response.json()["author"]["username"] == "testuser"
    assert response.json()["content_type"] == "anime"
    assert response.json()["status"] == "pending"
    assert response.json()["moderator"] is None
    assert response.json()["before"] is None
    assert response.json()["edit_id"] == 18

    # Now create one more edit for person
    response = await request_create_edit(
        client,
        get_test_token,
        "person",
        "justin-cook-77f1b3",
        {
            "after": {"name_ua": "Джастін Кук"},
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_200_OK

    # And now check if SQLAlchemy's polymorphic identity works
    edits = (
        await test_session.scalars(
            select(Edit).filter(Edit.system_edit == False)  # noqa: E712
        )
    ).all()

    assert isinstance(edits[0], AnimeEdit)
    assert edits[0].content_type == constants.CONTENT_ANIME

    assert isinstance(edits[1], PersonEdit)
    assert edits[1].content_type == constants.CONTENT_PERSON


async def test_edit_create_bad_after(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    get_dummy_token,
    test_session,
):
    # Create empty edit for anime
    response = await request_create_edit(
        client,
        get_dummy_token,
        "anime",
        "bocchi-the-rock-9e172d",
        {
            "description": "Empty edit",
            "after": {"title_en": "Bocchi the Rock!"},
        },
    )

    # Check status
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "edit:empty_edit"


async def test_edit_create_bad_permission(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user_banned,
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


async def test_edit_create_bad_content(
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
        "rock-the-bocchi-9e172d",
        {
            "description": "Brief description",
            "after": {"title_en": "Bocchi the Rock!"},
        },
    )

    # Check status
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "edit:content_not_found"


async def test_edit_create_bad_edit(
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
            "after": {"title_bad": "Bocchi The Rock!"},
        },
    )

    # Check status
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "edit:bad_edit"


async def test_edit_create_empty_edit(
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
            "after": {},
        },
    )

    # Check status
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"
