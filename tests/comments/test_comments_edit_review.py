from client_requests import request_comments_write
from client_requests import request_comments_edit
from client_requests import request_create_edit
from app.models import Comment, Review
from sqlalchemy import select, func
from fastapi import status
import asyncio


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


async def test_comments_edit_review_parallel(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # Two regular comments for same anime
    texts = {}

    for text in ["Перший коментар", "Другий коментар"]:
        response = await request_comments_write(
            client,
            get_test_token,
            "anime",
            "bocchi-the-rock-9e172d",
            text,
        )

        assert response.status_code == status.HTTP_200_OK
        texts[response.json()["reference"]] = text

    # Both of them are turned into review at once
    references = list(texts.keys())

    responses = await asyncio.gather(
        *[
            request_comments_edit(
                client,
                get_test_token,
                reference,
                "Тепер це огляд",
                review={"recommended": "yes"},
            )
            for reference in references
        ]
    )

    # Only one of them should become review
    status_codes = [response.status_code for response in responses]
    assert status_codes.count(status.HTTP_200_OK) == 1

    review_count = await test_session.scalar(select(func.count(Review.id)))
    assert review_count == 1

    for reference, response in zip(references, responses):
        comment = await test_session.scalar(
            select(Comment).filter(Comment.id == reference)
        )

        if response.status_code == status.HTTP_200_OK:
            assert comment.text == "Тепер це огляд"
            continue

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["code"] == "review:has_review"

        # Rejected edit shouldn't change comment text
        assert comment.text == texts[reference]
