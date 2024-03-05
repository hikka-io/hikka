from client_requests import request_create_collection
from client_requests import request_collections_list
from fastapi import status


async def test_collections_list(
    client,
    aggregator_anime,
    aggregator_anime_info,
    aggregator_people,
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

    people_slugs = [
        "justin-cook-77f1b3",
        "hiroo-maruyama-452304",
        "noritomo-yonai-02c2c8",
        "yasuhiro-irie-5b4e11",
        "masafumi-mima-b802cd",
        "ikehata-hiroshi-e166f7",
        "takahiro-ikezoe-c42cb5",
        "kenshirou-morii-ad1c5b",
    ]

    response = await request_create_collection(
        client,
        get_test_token,
        {
            "tags": [],
            "title": "Random anime collection",
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
                for index, slug in enumerate(anime_slugs)
            ],
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_200_OK

    response = await request_create_collection(
        client,
        get_test_token,
        {
            "tags": [],
            "title": "Random people collection",
            "description": "Description",
            "content_type": "person",
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
                for index, slug in enumerate(people_slugs)
            ],
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_200_OK

    # Now let's get list of collections
    response = await request_collections_list(client)

    assert len(response.json()["list"]) == 2
    assert response.json()["list"][0]["title"] == "Random people collection"
    assert response.json()["list"][1]["title"] == "Random anime collection"

    # Check preview length
    assert len(response.json()["list"][0]["collection"]) == 6
    assert len(response.json()["list"][1]["collection"]) == 6

    # Check anime slugs just in case
    assert (
        response.json()["list"][1]["collection"][0]["content"]["slug"]
        == anime_slugs[0]
    )

    assert (
        response.json()["list"][1]["collection"][5]["content"]["slug"]
        == anime_slugs[5]
    )

    # As well as person slugs
    assert (
        response.json()["list"][0]["collection"][0]["content"]["slug"]
        == people_slugs[0]
    )

    assert (
        response.json()["list"][0]["collection"][5]["content"]["slug"]
        == people_slugs[5]
    )
