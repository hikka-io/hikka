from client_requests import request_create_collection
from client_requests import request_collections
from fastapi import status
from app import constants


async def test_collections_list_content(
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

    other_anime_slugs = [
        "shingeki-no-kyojin-0cf69a",
        "shingeki-no-kyojin-season-3-b22bb3",
    ]

    for title, slugs in [
        ("Random anime collection", anime_slugs),
        ("Another anime collection", other_anime_slugs),
    ]:
        response = await request_create_collection(
            client,
            get_test_token,
            {
                "tags": ["tag"],
                "title": title,
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

        # Make sure we got correct response code
        assert response.status_code == status.HTTP_200_OK

    # Content within preview (first 6 entries) should be found
    response = await request_collections(
        client, filters={"content_type": "anime", "content": [anime_slugs[0]]}
    )

    assert response.json()["pagination"]["total"] == 1
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["title"] == "Random anime collection"

    # Content outside of preview should be found as well
    response = await request_collections(
        client, filters={"content_type": "anime", "content": [anime_slugs[7]]}
    )

    assert response.json()["pagination"]["total"] == 1
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["title"] == "Random anime collection"

    # Preview is still limited to 6 entries
    assert len(response.json()["list"][0]["collection"]) == 6

    # Collections without specified content should not be returned
    response = await request_collections(
        client,
        filters={"content_type": "anime", "content": [other_anime_slugs[0]]},
    )

    assert response.json()["pagination"]["total"] == 1
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["title"] == "Another anime collection"

    # Unknown slug should be rejected
    response = await request_collections(
        client,
        filters={"content_type": "anime", "content": ["bad-slug-000000"]},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:bad_content"

    # Content filter without content type should be rejected as well
    response = await request_collections(
        client, filters={"content": [anime_slugs[0]]}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:empty_content_type"
