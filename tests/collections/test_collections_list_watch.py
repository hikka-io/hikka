from client_requests import request_create_collection
from client_requests import request_collections_list
from client_requests import request_watch_add
from fastapi import status
from app import constants


async def test_collections_list_watch(
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

    await request_watch_add(
        client,
        "fullmetal-alchemist-brotherhood-fc524a",
        get_test_token,
        {"status": "watching", "episodes": 1},
    )

    # Now let's get list of collections
    response = await request_collections_list(client, token=get_test_token)

    watch_data = response.json()["list"][0]["collection"][0]["content"]["watch"]

    assert len(watch_data) == 1

    assert watch_data[0]["status"] == "watching"
    assert watch_data[0]["rewatches"] == 0
    assert watch_data[0]["duration"] == 24
    assert watch_data[0]["episodes"] == 1
    assert watch_data[0]["note"] is None

    # And one more time but without auth
    response = await request_collections_list(client)

    watch_data = response.json()["list"][0]["collection"][0]["content"]["watch"]

    assert len(watch_data) == 0
