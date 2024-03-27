from client_requests import request_create_collection
from client_requests import request_collections
from client_requests import request_vote
from fastapi import status
from app import constants


async def test_collections_list_vote(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
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
            "visibility": constants.COLLECTION_PUBLIC,
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

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_200_OK

    # Now let's get list of collections
    response = await request_collections(client, token=get_test_token)

    # Score should be zero
    assert response.json()["list"][0]["vote_score"] == 0
    assert response.json()["list"][0]["my_score"] == 0

    await request_vote(
        client,
        get_test_token,
        constants.CONTENT_COLLECTION,
        response.json()["list"][0]["reference"],
        1,
    )

    # Let's get collections list again
    response = await request_collections(client, token=get_test_token)

    # Let's check socre again
    assert response.json()["list"][0]["vote_score"] == 1
    assert response.json()["list"][0]["my_score"] == 1
