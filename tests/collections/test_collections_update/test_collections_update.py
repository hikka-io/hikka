from client_requests import request_create_collection
from client_requests import request_update_collection
from fastapi import status


async def test_collections_update(
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

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_200_OK

    collection_reference = response.json()["reference"]

    response = await request_update_collection(
        client,
        collection_reference,
        get_test_token,
        {
            "title": "Test collection 2",
            "tags": ["comedy", "romance"],
            "content_type": "anime",
            "description": "Description 2",
            "labels_order": ["Great", "Good"],
            "private": True,
            "spoiler": True,
            "nsfw": True,
            "content": [
                {
                    "slug": "bocchi-the-rock-9e172d",
                    "comment": "Author comment",
                    "label": "Great",
                    "order": 1,
                },
                {
                    "slug": "fullmetal-alchemist-brotherhood-fc524a",
                    "comment": None,
                    "label": "Good",
                    "order": 2,
                },
            ],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["title"] == "Test collection 2"
    assert response.json()["tags"] == ["comedy", "romance"]
    assert response.json()["description"] == "Description 2"
    assert response.json()["labels_order"] == ["Great", "Good"]
    assert response.json()["private"] is True
    assert response.json()["spoiler"] is True
    assert response.json()["nsfw"] is True

    assert (
        response.json()["collection"][0]["content"]["slug"]
        == "bocchi-the-rock-9e172d"
    )

    assert (
        response.json()["collection"][1]["content"]["slug"]
        == "fullmetal-alchemist-brotherhood-fc524a"
    )
