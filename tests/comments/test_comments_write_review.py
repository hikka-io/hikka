from client_requests import request_comments_write
from client_requests import request_comments_hide
from client_requests import request_create_edit
from app.models import Comment, Review
from sqlalchemy import select, func
from fastapi import status
import asyncio


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

    review = await test_session.scalar(select(Review))
    assert review is not None
    assert review.recommended == "yes"


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
    assert response.json()["code"] == "permission:confirm_email"


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


async def test_comments_write_review_after_deletion(
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

    # Now delete comment with original review
    response = await request_comments_hide(
        client, get_test_token, response.json()["reference"]
    )

    assert response.status_code == status.HTTP_200_OK

    # And write review for same content again
    response = await request_comments_write(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        "Ого, класне аніме, прям я!",
        review={"recommended": "yes"},
    )

    assert response.status_code == status.HTTP_200_OK


async def test_comments_write_review_parallel(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    comments_before = await test_session.scalar(select(func.count(Comment.id)))

    # Same user writes several reviews for same anime at once
    responses = await asyncio.gather(
        *[
            request_comments_write(
                client,
                get_test_token,
                "anime",
                "bocchi-the-rock-9e172d",
                f"Огляд номер {index}",
                review={"recommended": "yes"},
            )
            for index in range(3)
        ]
    )

    # Only one of them should be saved
    status_codes = [response.status_code for response in responses]
    assert status_codes.count(status.HTTP_200_OK) == 1

    for response in responses:
        if response.status_code != status.HTTP_200_OK:
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["code"] == "review:has_review"

    review_count = await test_session.scalar(select(func.count(Review.id)))
    assert review_count == 1

    # Rejected reviews shouldn't leave their comments behind
    comments_after = await test_session.scalar(select(func.count(Comment.id)))
    assert comments_after - comments_before == 1
