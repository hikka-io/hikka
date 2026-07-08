from client_requests import request_comments_write
from client_requests import request_watch_delete
from client_requests import request_watch_add
from app.sync.history import generate_history
from sqlalchemy import select
from app.models import Review
from fastapi import status


async def test_history_watch_review_score(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    slug = "bocchi-the-rock-9e172d"

    # Add anime to watch list with an initial score
    response = await request_watch_add(
        client,
        slug,
        get_test_token,
        {
            "status": "watching",
            "note": "Test",
            "episodes": 10,
            "score": 8,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    # Write review for the same anime
    response = await request_comments_write(
        client,
        get_test_token,
        "anime",
        slug,
        "Ого, класне аніме, прям я!",
        review={"recommended": "yes"},
    )

    assert response.status_code == status.HTTP_200_OK

    # After creation score should be cached from the watch list entry
    review = await test_session.scalar(select(Review))
    assert review is not None
    assert review.score == 8

    # Now user updates his score on the watch list
    response = await request_watch_add(
        client,
        slug,
        get_test_token,
        {
            "status": "watching",
            "note": "Test",
            "episodes": 10,
            "score": 5,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    # Sync task should propagate the new score to the cached review value
    await generate_history(test_session)

    review = await test_session.scalar(select(Review))
    assert review.score == 5

    # Finally user removes the anime from his watch list
    response = await request_watch_delete(client, slug, get_test_token)
    assert response.status_code == status.HTTP_200_OK

    # Sync task should reset cached review score back to zero
    await generate_history(test_session)

    review = await test_session.scalar(select(Review))
    assert review.score == 0
