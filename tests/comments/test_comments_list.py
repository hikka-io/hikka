from client_requests import request_comments_list_flat
from client_requests import request_comments_write
from client_requests import request_comments_list
from client_requests import request_vote
from fastapi import status
from app import constants


async def test_comments_list(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    parent_comment = None

    for index, text in enumerate(range(1, 5)):
        response = await request_comments_write(
            client, get_test_token, "edit", "17", str(text), parent_comment
        )

        if index == 0:
            await request_vote(
                client,
                get_test_token,
                constants.CONTENT_COMMENT,
                parent_comment,
                1,
            )

        parent_comment = response.json()["reference"]

    response = await request_comments_list(client, "edit", "17")

    # Check status
    assert response.status_code == status.HTTP_200_OK

    assert response.json()["list"][0]["text"] == "1"
    assert response.json()["list"][0]["my_score"] == 0
    assert response.json()["list"][0]["replies"][0]["text"] == "2"
    assert response.json()["list"][0]["replies"][0]["my_score"] == 0
    assert response.json()["list"][0]["replies"][0]["replies"][0]["text"] == "3"
    assert response.json()["list"][0]["is_editable"] is True
    assert (
        response.json()["list"][0]["replies"][0]["replies"][0]["replies"][0][
            "text"
        ]
        == "4"
    )


async def test_comments_list_authorized(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    parent_comment = None

    for index, text in enumerate(range(1, 5)):
        response = await request_comments_write(
            client, get_test_token, "edit", "17", str(text), parent_comment
        )

        if index == 1:
            await request_vote(
                client,
                get_test_token,
                constants.CONTENT_COMMENT,
                response.json()["reference"],
                1,
            )

        if index == 2:
            await request_vote(
                client,
                get_test_token,
                constants.CONTENT_COMMENT,
                response.json()["reference"],
                -1,
            )

        parent_comment = response.json()["reference"]

    response = await request_comments_list(client, "edit", "17", get_test_token)

    # Check status
    assert response.status_code == status.HTTP_200_OK

    assert response.json()["list"][0]["text"] == "1"
    assert response.json()["list"][0]["my_score"] == 0
    assert response.json()["list"][0]["replies"][0]["text"] == "2"
    assert response.json()["list"][0]["replies"][0]["my_score"] == 1
    assert response.json()["list"][0]["replies"][0]["replies"][0]["text"] == "3"
    assert (
        response.json()["list"][0]["replies"][0]["replies"][0]["my_score"] == -1
    )
    assert (
        response.json()["list"][0]["replies"][0]["replies"][0]["replies"][0][
            "text"
        ]
        == "4"
    )


async def test_comments_list_threads_replies(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    async def write(text, parent=None):
        response = await request_comments_write(
            client, get_test_token, "edit", "17", text, parent
        )

        assert response.status_code == status.HTTP_200_OK

        return response.json()["reference"]

    # Older thread has more replies than flat list shows
    first = await write("First")

    for index in range(1, 13):
        await write(f"First {index}", first)

    # Newer thread with nested reply
    second = await write("Second")
    second_reply = await write("Second 1", second)
    await write("Second 1 1", second_reply)
    await write("Second 2", second)

    # Flat list shows each thread followed by its first 10 replies
    response = await request_comments_list_flat(client, "edit", "17")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2

    assert [comment["text"] for comment in response.json()["list"]] == [
        "Second",
        "Second 1",
        "Second 1 1",
        "Second 2",
        "First",
        *[f"First {index}" for index in range(1, 11)],
    ]

    # Legacy list still returns whole threads
    response = await request_comments_list(client, "edit", "17")

    assert response.status_code == status.HTTP_200_OK

    second_thread, first_thread = response.json()["list"]

    assert [reply["text"] for reply in first_thread["replies"]] == [
        f"First {index}" for index in range(1, 13)
    ]

    assert [reply["text"] for reply in second_thread["replies"]] == [
        "Second 1",
        "Second 2",
    ]

    assert second_thread["replies"][0]["replies"][0]["text"] == "Second 1 1"
