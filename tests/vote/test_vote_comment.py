from client_requests import request_comments_write
from client_requests import request_vote_status
from sqlalchemy import select, desc, func
from app.models import Comment, Vote, Log
from client_requests import request_vote
from fastapi import status
from app import constants
import asyncio


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


async def test_vote_comment_parallel(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "Text"
    )

    comment_reference = response.json()["reference"]

    # Same vote sent from several requests at once
    responses = await asyncio.gather(
        *[
            request_vote(
                client,
                get_test_token,
                constants.CONTENT_COMMENT,
                comment_reference,
                1,
            )
            for _ in range(5)
        ]
    )

    for response in responses:
        assert response.status_code == status.HTTP_200_OK

    # User should have only one vote for comment
    vote_count = await test_session.scalar(
        select(func.count(Vote.id)).filter(Vote.user == create_test_user)
    )

    assert vote_count == 1

    # And it should be counted only once
    comment = await test_session.scalar(
        select(Comment).filter(Comment.id == comment_reference)
    )

    assert comment.vote_score == 1
