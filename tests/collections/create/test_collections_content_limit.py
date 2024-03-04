from client_requests import request_create_collection
from fastapi import status


async def test_collections_create_content_limit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client,
        get_test_token,
        {
            "title": "Test collection",
            "tags": ["romance", "comedy"],
            "content_type": "anime",
            "description": "Description",
            "labels_order": [],
            "private": False,
            "spoiler": False,
            "nsfw": False,
            "content": [],
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:content_limit"
