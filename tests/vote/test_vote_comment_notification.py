from app.sync.notifications import generate_notifications
from client_requests import request_comments_write
from client_requests import request_notifications
from client_requests import request_vote
from app import constants


async def test_vote_comment_notification(
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

    await request_vote(
        client,
        get_dummy_token,
        constants.CONTENT_COMMENT,
        comment_reference,
        -1,
    )

    await generate_notifications(test_session)

    response = await request_notifications(client, get_test_token)

    assert response.json()["list"][0]["initiator_user"] is None
