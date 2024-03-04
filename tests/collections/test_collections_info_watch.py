from client_requests import request_create_collection
from client_requests import request_collection_info
from client_requests import request_watch_add
from fastapi import status


async def test_collections_info_watch(
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
            "tags": [],
            "title": "Test collection",
            "description": "Description",
            "content_type": "anime",
            "labels_order": [],
            "private": False,
            "spoiler": False,
            "nsfw": False,
            "content": [
                {
                    "slug": "fullmetal-alchemist-brotherhood-fc524a",
                    "comment": None,
                    "label": None,
                    "order": 1,
                }
            ],
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_200_OK

    await request_watch_add(
        client,
        "fullmetal-alchemist-brotherhood-fc524a",
        get_test_token,
        {"status": "watching", "episodes": 1},
    )

    # Get collection info
    response = await request_collection_info(
        client, response.json()["reference"], get_test_token
    )

    assert response.json()["collection"][0]["content"]["watch"][0]["score"] == 0
    assert len(response.json()["collection"][0]["content"]["watch"]) == 1

    assert (
        response.json()["collection"][0]["content"]["watch"][0]["status"]
        == "watching"
    )
    assert (
        response.json()["collection"][0]["content"]["watch"][0]["rewatches"]
        == 0
    )
    assert (
        response.json()["collection"][0]["content"]["watch"][0]["duration"]
        == 24
    )
    assert (
        response.json()["collection"][0]["content"]["watch"][0]["episodes"] == 1
    )
    assert (
        response.json()["collection"][0]["content"]["watch"][0]["note"] is None
    )
