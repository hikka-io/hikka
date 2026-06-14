from client_requests import request_comments_write
from client_requests import request_create_edit
from fastapi import status


async def test_comments_write_review(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # Just a regular review
    response = await request_comments_write(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        "Ого, класне аніме, прям я!",
        review={"recommended": "yes"},
    )

    assert response.status_code == status.HTTP_200_OK


async def test_comments_write_review_duplicate(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # First user writes review
    response = await request_comments_write(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        "Ого, класне аніме, прям я!",
        review={"recommended": "yes"},
    )

    assert response.status_code == status.HTTP_200_OK

    # Next one should fail since we only one review per title per user
    response = await request_comments_write(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        "Чому вона постійно дригається?",
        review={"recommended": "no"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "review:has_review"


async def test_comments_write_review_restricted(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user_restricted,
    get_dummy_token,
    test_session,
):
    # User must have permission to write reviews
    response = await request_comments_write(
        client,
        get_dummy_token,
        "anime",
        "bocchi-the-rock-9e172d",
        "Ого, класне аніме, прям я!",
        review={"recommended": "yes"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"


async def test_comments_write_review_no_parrent(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # Only top level comment can be a review
    response = await request_comments_write(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        "Тестовий батьківський комент",
    )

    parrent_comment_id = response.json()["reference"]

    response = await request_comments_write(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        "Спроба написати огляд під батьківським коментарем",
        parrent_comment_id,
        {"recommended": "yes"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "review:no_parent"


async def test_comments_write_review_not_reviewable(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # We only allow reviews for anime/manga/novels
    await request_create_edit(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        {
            "description": "Brief description",
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    response = await request_comments_write(
        client,
        get_test_token,
        "edit",
        "18",
        "Ого, класна правка",
        review={"recommended": "yes"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "review:non_reviewable_content"
