from client_requests import request_comments_write
from client_requests import request_comments_hide
from client_requests import request_comments_list
from sqlalchemy.orm import selectinload
from app.models import Comment, Log
from sqlalchemy import select, desc
from fastapi import status
from app import constants


async def test_comments_hide_replies(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # Top level comment
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "Hello there"
    )

    comment_reference = response.json()["reference"]

    # Now make sure comment is present in list
    response = await request_comments_list(client, "edit", "17")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1

    # Hide comment
    await request_comments_hide(client, get_test_token, comment_reference)

    # Check whether first level comment is gone
    response = await request_comments_list(client, "edit", "17")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 0

    # One more time
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "Hello there"
    )

    top_comment_reference = response.json()["reference"]

    response = await request_comments_write(
        client,
        get_test_token,
        "edit",
        "17",
        "General Kenobi",
        top_comment_reference,
    )

    middle_comment_reference = response.json()["reference"]

    response = await request_comments_write(
        client,
        get_test_token,
        "edit",
        "17",
        "You are a bold one",
        middle_comment_reference,
    )

    last_comment_reference = response.json()["reference"]

    # Verify we have all 3 comments
    response = await request_comments_list(client, "edit", "17")
    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["list"]) == 1
    assert len(response.json()["list"][0]["replies"]) == 1
    assert len(response.json()["list"][0]["replies"][0]["replies"]) == 1
    assert response.json()["list"][0]["replies"][0]["hidden"] is False

    # Hide middle comment
    await request_comments_hide(
        client, get_test_token, middle_comment_reference
    )

    # Now check again, still should be 3
    response = await request_comments_list(client, "edit", "17")
    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["list"]) == 1
    assert len(response.json()["list"][0]["replies"]) == 1
    assert len(response.json()["list"][0]["replies"][0]["replies"]) == 1
    assert response.json()["list"][0]["replies"][0]["hidden"] is True

    # Now hide last one
    await request_comments_hide(client, get_test_token, last_comment_reference)

    # Should be only one comment
    response = await request_comments_list(client, "edit", "17")
    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["list"]) == 1
    assert len(response.json()["list"][0]["replies"]) == 0
