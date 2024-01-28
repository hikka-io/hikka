from client_requests import request_comments_write
from client_requests import request_comments_edit
from app.models import Comment
from datetime import timedelta
from sqlalchemy import select
from fastapi import status


async def test_comments_edit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "Old text"
    )

    response = await request_comments_edit(
        client, get_test_token, response.json()["reference"], "New text"
    )

    # Check status
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["text"] == "New text"


async def test_comments_edit_empty_markdown(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "Old text"
    )

    response = await request_comments_edit(
        client, get_test_token, response.json()["reference"], "[empty]()"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_comments_edit_rate_limit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "Old text"
    )

    for index, _ in enumerate(range(0, 5)):
        await request_comments_edit(
            client, get_test_token, response.json()["reference"], "New text"
        )

        if index != 5:
            continue

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["code"] == "comment:max_edits"


async def test_comments_edit_time_limit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "Old text"
    )

    comment = await test_session.scalar(
        select(Comment).filter(Comment.id == response.json()["reference"])
    )

    # Send comment back in time to test time limit
    comment.created = comment.created - timedelta(hours=1)
    test_session.add(comment)
    await test_session.commit()

    response = await request_comments_edit(
        client, get_test_token, response.json()["reference"], "New text"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "comment:edit_time_limit"


async def test_comments_edit_bad_author(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    create_dummy_user,
    get_dummy_token,
    get_test_token,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "Old text"
    )

    response = await request_comments_edit(
        client, get_dummy_token, response.json()["reference"], "New text"
    )

    # Check status
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "comment:not_owner"
