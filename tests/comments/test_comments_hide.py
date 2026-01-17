from client_requests import request_comments_write
from client_requests import request_comments_hide
from sqlalchemy.orm import selectinload
from app.models import Comment, Log
from sqlalchemy import select, desc
from fastapi import status
from app import constants


async def test_comments_hide(
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

    comment_reference = response.json()["reference"]

    response = await request_comments_hide(
        client, get_test_token, comment_reference
    )

    # Check status
    assert response.status_code == status.HTTP_200_OK

    comment = await test_session.scalar(
        select(Comment)
        .filter(Comment.id == comment_reference)
        .options(selectinload(Comment.hidden_by))
    )

    assert comment.hidden is True
    assert comment.hidden_by.username == "testuser"

    # Now let's try hide it one more time
    response = await request_comments_hide(
        client, get_test_token, comment_reference
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "comment:already_hidden"

    # Check comment hide log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_COMMENT_HIDE
    assert log.data == {"content_type": "edit"}
    assert log.user == create_test_user
    assert log.user == comment.author


async def test_comments_hide_admin(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_admin,
    create_dummy_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    response = await request_comments_write(
        client, get_dummy_token, "edit", "17", "Old text"
    )

    comment_reference = response.json()["reference"]

    response = await request_comments_hide(
        client, get_test_token, comment_reference
    )

    # Check status
    assert response.status_code == status.HTTP_200_OK

    comment = await test_session.scalar(
        select(Comment)
        .filter(Comment.id == comment_reference)
        .options(selectinload(Comment.hidden_by))
    )

    assert comment.hidden is True
    assert comment.hidden_by.username == "testuser"

    # Check comment hide log by admin
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_COMMENT_HIDE
    assert log.user == create_test_user_admin
    assert log.data == {"content_type": "edit"}
    assert log.user != comment.author


async def test_comments_hide_bad_admin(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    create_dummy_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    response = await request_comments_write(
        client, get_dummy_token, "edit", "17", "Old text"
    )

    comment_reference = response.json()["reference"]

    response = await request_comments_hide(
        client, get_test_token, comment_reference
    )

    # Check status
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"
