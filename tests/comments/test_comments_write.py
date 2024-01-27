from client_requests import request_comments_write
from fastapi import status


async def test_comments_write(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_moderator,
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

    parent_comment = response.json()["reference"]

    for index, text in enumerate(["First", "Second", "Third", "Fourth"]):
        response = await request_comments_write(
            client, get_test_token, "edit", "17", text, parent_comment
        )

        if index < 3:
            assert response.status_code == status.HTTP_200_OK
            parent_comment = response.json()["reference"]

        else:
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["code"] == "comment:max_depth"


async def test_comments_write_bad_content(
    client,
    create_test_user_moderator,
    get_test_token,
    test_session,
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
    create_test_user_moderator,
    get_test_token,
    test_session,
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


async def test_comments_rate_limit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_moderator,
    get_test_token,
    test_session,
):
    comments_limit = 100

    for index, _ in enumerate(range(0, comments_limit)):
        response = await request_comments_write(
            client, get_test_token, "edit", "17", f"{index} comment, yay!"
        )

        if index == comments_limit:
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["code"] == "comment:rate-limit"


async def test_comments_empty_markdown(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_moderator,
    get_test_token,
    test_session,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "[empty]()"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "comment:empty_markdown"
