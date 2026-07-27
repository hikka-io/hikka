from client_requests import request_comments_write
from client_requests import request_comments_edit
from client_requests import request_comments_hide
from client_requests import request_anime_info
from fastapi import status


async def test_comments_review_stats(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    create_dummy_user,
    get_test_token,
    get_dummy_token,
    test_session,
):
    slug = "bocchi-the-rock-9e172d"

    # No reviews yet, so everything should be zeroed out
    response = await request_anime_info(client, slug)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["review_stats"] == {"yes": 0, "no": 0, "maybe": 0}

    # First review bumps the counter it was written with
    response = await request_comments_write(
        client,
        get_test_token,
        "anime",
        slug,
        "Ого, класне аніме, прям я!",
        review={"recommended": "yes"},
    )

    assert response.status_code == status.HTTP_200_OK
    comment_reference = response.json()["reference"]

    response = await request_anime_info(client, slug)
    assert response.json()["review_stats"] == {"yes": 1, "no": 0, "maybe": 0}

    # Second user writes review with different recommendation
    response = await request_comments_write(
        client,
        get_dummy_token,
        "anime",
        slug,
        "Чому вона постійно дригається?",
        review={"recommended": "no"},
    )

    assert response.status_code == status.HTTP_200_OK
    dummy_comment_reference = response.json()["reference"]

    response = await request_anime_info(client, slug)
    assert response.json()["review_stats"] == {"yes": 1, "no": 1, "maybe": 0}

    # Changing recommendation moves the count between buckets
    response = await request_comments_edit(
        client,
        get_test_token,
        comment_reference,
        "Ого, класне аніме, прям я!",
        review={"recommended": "maybe"},
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_anime_info(client, slug)
    assert response.json()["review_stats"] == {"yes": 0, "no": 1, "maybe": 1}

    # Dropping review from comment should remove it from stats
    response = await request_comments_edit(
        client,
        get_test_token,
        comment_reference,
        "Ого, класне аніме, прям я!",
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_anime_info(client, slug)
    assert response.json()["review_stats"] == {"yes": 0, "no": 1, "maybe": 0}

    # And hiding comment with review should do the same
    response = await request_comments_hide(
        client, get_dummy_token, dummy_comment_reference
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_anime_info(client, slug)
    assert response.json()["review_stats"] == {"yes": 0, "no": 0, "maybe": 0}
