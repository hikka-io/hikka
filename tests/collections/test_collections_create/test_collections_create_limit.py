from client_requests import request_create_collection
from fastapi import status


async def test_collections_create_limit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    collections_limit = 10

    for step in range(0, collections_limit + 1):
        response = await request_create_collection(
            client,
            get_test_token,
            {
                "title": "Test collection",
                "tags": ["romance", "comedy"],
                "content_type": "anime",
                "description": "Description",
                "labels_order": ["Good", "Great"],
                "private": False,
                "spoiler": False,
                "nsfw": False,
                "content": [
                    {
                        "slug": "fullmetal-alchemist-brotherhood-fc524a",
                        "comment": None,
                        "label": "Good",
                        "order": 1,
                    },
                    {
                        "slug": "bocchi-the-rock-9e172d",
                        "comment": "Author comment",
                        "label": "Great",
                        "order": 2,
                    },
                ],
            },
        )

        if step < collections_limit:
            assert response.status_code == status.HTTP_200_OK

        else:
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["code"] == "collections:limit"
