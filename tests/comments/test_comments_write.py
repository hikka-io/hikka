from client_requests import request_comments_write
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_comments_write(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "First comment, yay!"
    )

    # Check status
    assert response.status_code == status.HTTP_200_OK

    assert response.json()["author"]["username"] == "testuser"
    assert response.json()["text"] == "First comment, yay!"
    assert response.json()["total_replies"] == 0

    assert response.json()["preview"]["slug"] == "17"

    # Check first comment log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_COMMENT_WRITE
    assert log.data == {"content_type": "edit"}
    assert log.user == create_test_user

    parent_comment = response.json()["reference"]

    max_depth = 5

    for index, text in enumerate(range(1, max_depth)):
        response = await request_comments_write(
            client, get_test_token, "edit", "17", f"Test {text}", parent_comment
        )

        if index <= max_depth:
            assert response.status_code == status.HTTP_200_OK
            parent_comment = response.json()["reference"]
            continue

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["code"] == "comment:max_depth"


async def test_comments_write_bad_content(
    client,
    create_test_user,
    get_test_token,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "1", "Bad content"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "comment:content_not_found"


async def test_comments_write_bad_parent(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    response = await request_comments_write(
        client,
        get_test_token,
        "edit",
        "17",
        "Comment text",
        "6ca960d0-b84f-4769-bef5-b132c0211613",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "comment:parent_not_found"


async def test_comments_write_rate_limit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    comments_limit = 100

    for index, _ in enumerate(range(0, comments_limit)):
        response = await request_comments_write(
            client, get_test_token, "edit", "17", f"{index} comment, yay!"
        )

        if index == comments_limit:
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["code"] == "comment:rate-limit"


async def test_comments_write_empty_markdown(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "[empty]()"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_comments_write_bad_permission(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user_restricted,
    get_dummy_token,
):
    response = await request_comments_write(
        client, get_dummy_token, "edit", "17", "First comment, yay!"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"
