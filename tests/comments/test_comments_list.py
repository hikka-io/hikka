from client_requests import request_comments_write
from client_requests import request_comments_list
from client_requests import request_comments_vote
from fastapi import status


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
            await request_comments_vote(
                client, get_test_token, parent_comment, 1
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
            await request_comments_vote(
                client, get_test_token, response.json()["reference"], 1
            )

        if index == 2:
            await request_comments_vote(
                client, get_test_token, response.json()["reference"], -1
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
