from client_requests import request_create_collection
from client_requests import request_collection_info
from fastapi import status


async def test_collections_info(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
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
            "labels_order": [],
            "private": False,
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

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_200_OK

    # Get collection info
    response = await request_collection_info(
        client, response.json()["reference"]
    )

    assert response.json()["collection"][0]["content"]["watch"] == []
    assert len(response.json()["collection"]) == 8

    from pprint import pprint

    pprint(response.json()["collection"])

    for index, slug in enumerate(slugs):
        assert response.json()["collection"][index]["content"]["slug"] == slug
        assert response.json()["collection"][index]["order"] == index + 1
