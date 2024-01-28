from client_requests import request_comments_write
from client_requests import request_comments_vote
from app.models import Comment
from sqlalchemy import select


# ToDo: more tests (?)
async def test_comments_vote(
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

    assert comment.score == 0

    await request_comments_vote(client, get_test_token, comment_reference, 1)
    await test_session.refresh(comment)
    assert comment.score == 1

    await request_comments_vote(client, get_dummy_token, comment_reference, 1)
    await test_session.refresh(comment)
    assert comment.score == 2

    await request_comments_vote(client, get_test_token, comment_reference, -1)
    await request_comments_vote(client, get_dummy_token, comment_reference, -1)
    await test_session.refresh(comment)
    assert comment.score == -2
