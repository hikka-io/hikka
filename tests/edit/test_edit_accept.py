from client_requests import request_accept_edit
from client_requests import request_create_edit
from sqlalchemy.orm import selectinload
from sqlalchemy import select, desc
from fastapi import status
from app import constants

from app.models import (
    UserEditStats,
    Anime,
    Genre,
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


async def test_edit_accept_genres(
    client,
    aggregator_genres,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    create_test_user_moderator,
    get_test_token,
    moderator_token,
    test_session,
):
    """
    Tests the full workflow of creating and accepting an edit that changes content genres.
    """
    # Define the anime and the genre changes
    anime_slug = "bocchi-the-rock-9e172d"
    new_genres_slugs = ["comedy", "music", "slice-of-life"]

    # Get the initial state of the anime's genres for later comparison
    anime = await test_session.scalar(
        select(Anime)
        .filter(Anime.slug == anime_slug)
        .options(selectinload(Anime.genres))
    )
    initial_genre_slugs = {genre.slug for genre in anime.genres}

    # Create an edit to change the genres
    response = await request_create_edit(
        client,
        get_test_token,
        "anime",
        anime_slug,
        {
            "description": "Adding slice-of-life genre",
            "after": {"genres": new_genres_slugs},
        },
    )

    assert response.status_code == status.HTTP_200_OK
    edit_id = response.json()["edit_id"]

    # Accept the edit with a moderator token
    response = await request_accept_edit(client, moderator_token, edit_id)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == constants.EDIT_ACCEPTED

    # Refresh the anime object from the database to get the updated state
    await test_session.refresh(
        anime, attribute_names=["genres", "ignored_fields", "needs_search_update"]
    )

    # Verify that the genres have been correctly updated
    updated_genre_slugs = {genre.slug for genre in anime.genres}
    assert updated_genre_slugs == set(new_genres_slugs)

    # Verify that 'genres' is now in ignored_fields and needs a search update
    assert "genres" in anime.ignored_fields
    assert anime.needs_search_update is True

    # Verify that the 'before' field in the Edit object was correctly recorded
    edit = await test_session.scalar(select(Edit).filter(Edit.edit_id == edit_id))
    assert edit is not None
    assert set(edit.before["genres"]) == initial_genre_slugs
