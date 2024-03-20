from client_requests import request_create_collection
from client_requests import request_favourite_list
from client_requests import request_favourite_add
from fastapi import status
from app import constants


async def test_favourite_list_anime(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    # User favourite list should be empty when we start
    response = await request_favourite_list(client, "anime", "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 0

    # Add anime to favourite
    await request_favourite_add(
        client, "anime", "kimi-no-na-wa-945779", get_test_token
    )

    # Now let's check again
    response = await request_favourite_list(client, "anime", "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["slug"] == "kimi-no-na-wa-945779"

    # Add one more anime to favourite
    await request_favourite_add(
        client, "anime", "oshi-no-ko-421060", get_test_token
    )

    # Now let's check again (again)
    response = await request_favourite_list(client, "anime", "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 2
    assert response.json()["list"][0]["slug"] == "oshi-no-ko-421060"
    assert response.json()["list"][1]["slug"] == "kimi-no-na-wa-945779"


async def test_favourite_list_collections(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    # First we create test anime collection
    response = await request_create_collection(
        client,
        get_test_token,
        {
            "title": "Test collection",
            "tags": ["romance", "comedy"],
            "content_type": "anime",
            "description": "Description",
            "labels_order": ["Good", "Great"],
            "visibility": constants.COLLECTION_PUBLIC,
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

    collection_reference = response.json()["reference"]

    # User favourite list should be empty when we start
    response = await request_favourite_list(client, "collection", "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 0

    # Add collection to favourite
    await request_favourite_add(
        client, "collection", collection_reference, get_test_token
    )

    # Now let's check again
    response = await request_favourite_list(client, "collection", "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["reference"] == collection_reference


async def test_favourite_list_collections_private(
    client,
    create_dummy_user,
    create_test_user,
    aggregator_anime,
    get_dummy_token,
    get_test_token,
):
    # First we create test anime collection
    response = await request_create_collection(
        client,
        get_test_token,
        {
            "title": "Test collection",
            "tags": ["romance", "comedy"],
            "content_type": "anime",
            "description": "Description",
            "labels_order": ["Good", "Great"],
            "visibility": constants.COLLECTION_PRIVATE,
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

    collection_reference = response.json()["reference"]

    # Add collection to favourite
    await request_favourite_add(
        client, "collection", collection_reference, get_test_token
    )

    # Now let's check user collections without auth
    response = await request_favourite_list(client, "collection", "testuser")

    assert response.json()["pagination"]["total"] == 0
    assert len(response.json()["list"]) == 0

    # Now let's check user collections with dummy user
    response = await request_favourite_list(
        client, "collection", "testuser", token=get_dummy_token
    )

    assert response.json()["pagination"]["total"] == 0
    assert len(response.json()["list"]) == 0

    # Now let's check user collections with author's token
    response = await request_favourite_list(
        client, "collection", "testuser", token=get_test_token
    )

    assert response.json()["pagination"]["total"] == 1
    assert len(response.json()["list"]) == 1
