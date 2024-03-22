from client_requests import request_comments_write
from client_requests import request_vote_status
from sqlalchemy import select, desc, func
from client_requests import request_vote
from app.models import Comment, Log
from fastapi import status
from app import constants


async def test_vote_comment(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "Text"
    )

    comment_reference = response.json()["reference"]

    comment = await test_session.scalar(
        select(Comment).filter(Comment.id == comment_reference)
    )

    assert comment.vote_score == 0

    await request_vote(
        client, get_test_token, constants.CONTENT_COMMENT, comment_reference, 1
    )

    await test_session.refresh(comment)
    assert comment.vote_score == 1

    # Before we move on let's check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_VOTE_SET
    assert log.user == create_test_user

    assert log.data["content_type"] == "comment"
    assert log.data["user_score"] == 1
    assert log.data["old_score"] == 0
    assert log.data["new_score"] == 1

    await request_vote(
        client, get_dummy_token, constants.CONTENT_COMMENT, comment_reference, 1
    )

    await test_session.refresh(comment)
    assert comment.vote_score == 2

    await request_vote(
        client, get_test_token, constants.CONTENT_COMMENT, comment_reference, -1
    )

    await request_vote(
        client,
        get_dummy_token,
        constants.CONTENT_COMMENT,
        comment_reference,
        -1,
    )

    await test_session.refresh(comment)
    assert comment.vote_score == -2

    # Let's check total number of created vote logs because why not
    vote_logs_count = await test_session.scalar(
        select(func.count(Log.id)).filter(
            Log.log_type == constants.LOG_VOTE_SET
        )
    )

    # Should be four (right?)
    assert vote_logs_count == 4

    # And finally let's check vote status
    response = await request_vote_status(
        client, get_test_token, constants.CONTENT_COMMENT, comment_reference
    )

    # Check status and score
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["score"] == -1
