from client_requests import request_comments_write
from client_requests import request_comments_edit
from client_requests import request_create_edit
from sqlalchemy import select, func
from app.models import Review
from fastapi import status


async def test_comments_edit_review(
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

    response = await request_comments_edit(
        client,
        get_test_token,
        response.json()["reference"],
        "Ого, класне аніме, прям я!",
        review={"recommended": "no"},
    )

    assert response.status_code == status.HTTP_200_OK

    await test_session.refresh(review)
    assert review is not None
    assert review.recommended == "no"


async def test_comments_delete_review(
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

    response = await request_comments_edit(
        client,
        get_test_token,
        response.json()["reference"],
        "Ого, класне аніме, прям я!",
        review=None,
    )

    assert response.status_code == status.HTTP_200_OK

    review_count = await test_session.scalar(select(func.count(Review.id)))
    assert review_count == 0


async def test_comments_edit_review_not_reviewable(
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
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_comments_edit(
        client,
        get_test_token,
        response.json()["reference"],
        "Ого, класна правка, раджу!",
        review={"recommended": "yes"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
