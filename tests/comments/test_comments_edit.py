from client_requests import request_comments_write
from client_requests import request_comments_edit
from client_requests import request_comments_hide
from sqlalchemy import select, desc
from app.models import Comment, Log
from datetime import timedelta
from fastapi import status
from app import constants


async def test_comments_edit(
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

    response = await request_comments_edit(
        client, get_test_token, response.json()["reference"], "New text"
    )

    # Check status
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["text"] == "New text"

    # Check comment edit log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_COMMENT_EDIT
    assert log.user == create_test_user
    assert log.data["old_text"] == "Old text"
    assert log.data["new_text"] == "New text"


async def test_comments_edit_hidden(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "Old text"
    )

    comment_reference = response.json()["reference"]

    await request_comments_hide(client, get_test_token, comment_reference)

    response = await request_comments_edit(
        client, get_test_token, comment_reference, "New text"
    )

    # Check status
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "comment:hidden"


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


async def test_comments_edit_count_limit(
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

    comment = await test_session.scalar(
        select(Comment).filter(Comment.id == response.json()["reference"])
    )

    edit_count_limit = 500

    # Fill up fake history
    comment.history = list(range(edit_count_limit - 1))
    test_session.add(comment)
    await test_session.commit()

    await test_session.refresh(comment)
    assert comment.is_editable is True

    response = await request_comments_edit(
        client,
        get_test_token,
        response.json()["reference"],
        "New text editable",
    )

    assert response.status_code == status.HTTP_200_OK
    assert "code" not in response.json()

    await test_session.refresh(comment)
    assert comment.is_editable is False

    response = await request_comments_edit(
        client,
        get_test_token,
        response.json()["reference"],
        "New text uneditable",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "comment:not_editable"


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
    comment.created = comment.created - timedelta(hours=24)
    test_session.add(comment)
    await test_session.commit()

    assert comment.is_editable is False

    response = await request_comments_edit(
        client, get_test_token, response.json()["reference"], "New text"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "comment:not_editable"


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
