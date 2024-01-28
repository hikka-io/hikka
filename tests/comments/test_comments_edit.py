from client_requests import request_comments_write
from client_requests import request_comments_edit
from fastapi import status


async def test_comments_edit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_moderator,
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


async def test_comments_edit_empty_markdown(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_moderator,
    get_test_token,
    test_session,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "Old text"
    )

    response = await request_comments_edit(
        client, get_test_token, response.json()["reference"], "[empty]()"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"
