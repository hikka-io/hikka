from client_requests import request_comments_write
from client_requests import request_comments_user
from client_requests import request_comments_hide
from client_requests import request_vote
from fastapi import status
from app import constants


async def test_comments_user(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    create_dummy_user,
    get_test_token,
    get_dummy_token,
):
    parent_comment = None

    for text in range(1, 5):
        response = await request_comments_write(
            client, get_test_token, "edit", "17", str(text), parent_comment
        )

        parent_comment = response.json()["reference"]

    # Comment from another user should not be in the list
    await request_comments_write(
        client, get_dummy_token, "edit", "17", "Коментар від dummy"
    )

    response = await request_comments_user(client, "testuser")

    # Check status
    assert response.status_code == status.HTTP_200_OK

    # Comments are flat and sorted from newest to oldest
    assert response.json()["pagination"]["total"] == 4
    assert [comment["text"] for comment in response.json()["list"]] == [
        "4",
        "3",
        "2",
        "1",
    ]

    assert response.json()["list"][0]["replies"] == []
    assert response.json()["list"][0]["author"]["username"] == "testuser"
    assert response.json()["list"][0]["depth"] == 4
    assert response.json()["list"][3]["depth"] == 1


async def test_comments_user_first_level_only(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    parent_comment = None

    for text in range(1, 5):
        response = await request_comments_write(
            client, get_test_token, "edit", "17", str(text), parent_comment
        )

        parent_comment = response.json()["reference"]

    response = await request_comments_user(
        client, "testuser", first_level_only=True
    )

    # Check status
    assert response.status_code == status.HTTP_200_OK

    # Only top level comment should be returned
    assert response.json()["pagination"]["total"] == 1
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["text"] == "1"


async def test_comments_user_reviews(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    create_dummy_user,
    get_test_token,
    get_dummy_token,
):
    await request_comments_write(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        "Ого, класне аніме, прям я!",
        review={"recommended": "yes"},
    )

    await request_comments_write(
        client, get_test_token, "edit", "17", "Звичайний коментар"
    )

    # Review from another user should not affect filters
    await request_comments_write(
        client,
        get_dummy_token,
        "anime",
        "bocchi-the-rock-9e172d",
        "Чому вона постійно дригається?",
        review={"recommended": "no"},
    )

    # Only reviews
    response = await request_comments_user(
        client, "testuser", comment_type="review"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["text"] == "Ого, класне аніме, прям я!"
    assert response.json()["list"][0]["review"]["recommended"] == "yes"

    # Only comments
    response = await request_comments_user(
        client, "testuser", comment_type="comment"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["text"] == "Звичайний коментар"
    assert response.json()["list"][0]["review"] is None

    # Reviews with specific recommendation
    response = await request_comments_user(
        client, "testuser", recommended="yes"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["review"]["recommended"] == "yes"

    response = await request_comments_user(client, "testuser", recommended="no")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0
    assert response.json()["list"] == []


async def test_comments_user_authorized(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "Тестовий коментар"
    )

    await request_vote(
        client,
        get_test_token,
        constants.CONTENT_COMMENT,
        response.json()["reference"],
        1,
    )

    # Without token we should not see our score
    response = await request_comments_user(client, "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["my_score"] == 0

    response = await request_comments_user(client, "testuser", get_test_token)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["my_score"] == 1


async def test_comments_user_hidden(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    response = await request_comments_write(
        client, get_test_token, "edit", "17", "Прихований коментар"
    )

    await request_comments_hide(
        client, get_test_token, response.json()["reference"]
    )

    await request_comments_write(
        client, get_test_token, "edit", "17", "Звичайний коментар"
    )

    response = await request_comments_user(client, "testuser")

    # Check status
    assert response.status_code == status.HTTP_200_OK

    # Hidden comments should not be in the list
    assert response.json()["pagination"]["total"] == 1
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["text"] == "Звичайний коментар"


async def test_comments_user_bad_user(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    response = await request_comments_user(client, "unknown")

    # Check status
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "user:not_found"
