from client_requests import request_comments_write
from client_requests import request_companies_list
from fastapi import status


async def test_comments_list(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_moderator,
    get_test_token,
    test_session,
):
    parent_comment = None

    for text in ["First", "Second", "Third", "Fourth"]:
        response = await request_comments_write(
            client, get_test_token, "edit", "17", text, parent_comment
        )

        parent_comment = response.json()["reference"]

    response = await request_companies_list(client, "edit", "17")

    # Check status
    assert response.status_code == status.HTTP_200_OK

    assert response.json()["list"][0]["text"] == "First"
    assert response.json()["list"][0]["replies"][0]["text"] == "Second"
    assert (
        response.json()["list"][0]["replies"][0]["replies"][0]["text"]
        == "Third"
    )
    assert (
        response.json()["list"][0]["replies"][0]["replies"][0]["replies"][0][
            "text"
        ]
        == "Fourth"
    )
