from client_requests import request_create_collection
from client_requests import request_update_collection
from client_requests import request_comments_latest
from client_requests import request_comments_write
from app import constants


async def test_comments_write(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # First we create private collection
    slugs = [
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
            "title": "Test collection",
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
                for index, slug in enumerate(slugs)
            ],
        },
    )

    collection_reference = response.json()["reference"]

    # Then write comment for private collection
    await request_comments_write(
        client, get_test_token, "collection", collection_reference, "Comment"
    )

    # And get list of latest comment
    response = await request_comments_latest(client)
    assert len(response.json()) == 0

    # Make collection public
    response = await request_update_collection(
        client,
        collection_reference,
        get_test_token,
        {
            "tags": [],
            "title": "Test collection",
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
                for index, slug in enumerate(slugs)
            ],
        },
    )

    # Now there should be comment we wrote before
    response = await request_comments_latest(client)
    assert len(response.json()) == 1
