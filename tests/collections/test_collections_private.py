from client_requests import request_user_collections_list
from client_requests import request_create_collection
from client_requests import request_collections_list
from client_requests import request_collection_info
from fastapi import status
from app import constants


async def test_collections_list_private(
    client,
    aggregator_anime,
    aggregator_anime_info,
    aggregator_people,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    anime_slugs = [
        "fullmetal-alchemist-brotherhood-fc524a",
        "bocchi-the-rock-9e172d",
        "kaguya-sama-wa-kokurasetai-tensai-tachi-no-renai-zunousen-a3ac07",
        "kaguya-sama-wa-kokurasetai-tensai-tachi-no-renai-zunousen-73a73c",
        "kaguya-sama-wa-kokurasetai-ultra-romantic-fcd761",
        "kimi-no-na-wa-945779",
        "oshi-no-ko-421060",
        "steinsgate-f29797",
    ]

    response = await request_create_collection(
        client,
        get_test_token,
        {
            "tags": [],
            "title": "Random anime collection",
            "description": "Description",
            "content_type": "anime",
            "visibility": constants.COLLECTION_PRIVATE,
            "labels_order": [],
            "spoiler": False,
            "nsfw": False,
            "content": [
                {
                    "order": index + 1,
                    "comment": None,
                    "label": None,
                    "slug": slug,
                }
                for index, slug in enumerate(anime_slugs)
            ],
        },
    )

    collection_reference = response.json()["reference"]

    # Now let's get list of collections
    # And make sure that without auth there are none
    response = await request_collections_list(client)

    assert response.json()["pagination"]["total"] == 0
    assert len(response.json()["list"]) == 0

    # Now let's get list of collections by different user
    # Number of collections still should be zero
    response = await request_collections_list(client, token=get_dummy_token)

    assert response.json()["pagination"]["total"] == 0
    assert len(response.json()["list"]) == 0

    # And finally let's get list of collections by author
    # And there are still should be none
    response = await request_collections_list(client, token=get_test_token)

    assert response.json()["pagination"]["total"] == 0
    assert len(response.json()["list"]) == 0

    # Now we will check user's collections list
    # Private collection shouldn't be there
    response = await request_user_collections_list(client, "testuser")

    assert response.json()["pagination"]["total"] == 0
    assert len(response.json()["list"]) == 0

    # Now with auth from different user
    # Still should be zero
    response = await request_user_collections_list(
        client, "testuser", token=get_dummy_token
    )

    assert response.json()["pagination"]["total"] == 0
    assert len(response.json()["list"]) == 0

    # And finally let's check with author's auth token
    response = await request_user_collections_list(
        client, "testuser", token=get_test_token
    )

    assert response.json()["pagination"]["total"] == 1
    assert len(response.json()["list"]) == 1

    # Get private collection info without auth
    # Collection should not be found
    response = await request_collection_info(client, collection_reference)

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Get collection info with dummy user
    response = await request_collection_info(
        client, collection_reference, token=get_dummy_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Get collection info with author's token
    response = await request_collection_info(
        client, collection_reference, token=get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
