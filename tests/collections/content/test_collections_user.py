from client_requests import request_create_collection
from client_requests import request_collection_info
from client_requests import request_user_collections
from fastapi import status
from app import constants


async def test_collections_user(
    client,
    aggregator_anime,
    aggregator_anime_info,
    aggregator_people,
    create_anime_collection,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    await create_anime_collection(
        get_dummy_token, [("fullmetal-alchemist-brotherhood-fc524a", None)]
    )

    public_reference = await create_anime_collection(
        get_test_token,
        [
            ("fullmetal-alchemist-brotherhood-fc524a", None),
            ("bocchi-the-rock-9e172d", None),
        ],
        title="Alpha list",
    )

    private_reference = await create_anime_collection(
        get_test_token,
        [
            ("bocchi-the-rock-9e172d", "Great"),
            ("fullmetal-alchemist-brotherhood-fc524a", "Good"),
        ],
        ["Great", "Good"],
        visibility=constants.COLLECTION_PRIVATE,
        title="Beta list",
    )

    response = await request_create_collection(
        client,
        get_test_token,
        {
            "title": "People collection",
            "tags": [],
            "content_type": "person",
            "description": "Description",
            "labels_order": [],
            "visibility": constants.COLLECTION_PUBLIC,
            "spoiler": False,
            "nsfw": False,
            "content": [
                {
                    "slug": "justin-cook-77f1b3",
                    "comment": None,
                    "label": None,
                    "order": 1,
                }
            ],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_user_collections(
        client,
        get_test_token,
        "anime",
        content="fullmetal-alchemist-brotherhood-fc524a",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2

    private, public = response.json()["list"]

    assert set(private.keys()) == {
        "content_type",
        "content_label",
        "labels_order",
        "has_content",
        "visibility",
        "reference",
        "entries",
        "spoiler",
        "image",
        "title",
        "nsfw",
    }

    assert private["reference"] == private_reference
    assert private["visibility"] == constants.COLLECTION_PRIVATE
    assert private["labels_order"] == ["Great", "Good"]
    assert private["has_content"] is True
    assert private["content_label"] == "Good"
    assert private["entries"] == 2

    assert public["reference"] == public_reference
    assert public["has_content"] is True
    assert public["content_label"] is None

    info = await request_collection_info(
        client, private_reference, get_test_token
    )

    first_image = info.json()["collection"][0]["content"]["image"]
    assert first_image is not None
    assert private["image"] == first_image

    response = await request_user_collections(
        client, get_test_token, "anime", content="kimi-no-na-wa-945779"
    )

    assert [entry["has_content"] for entry in response.json()["list"]] == [
        False,
        False,
    ]

    response = await request_user_collections(client, get_test_token, "anime")

    assert response.status_code == status.HTTP_200_OK
    assert [entry["has_content"] for entry in response.json()["list"]] == [
        False,
        False,
    ]

    response = await request_user_collections(
        client, get_test_token, "anime", query="alpha"
    )

    assert [entry["reference"] for entry in response.json()["list"]] == [
        public_reference
    ]

    response = await request_user_collections(
        client, get_test_token, "anime", query="a"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = await request_user_collections(client, get_test_token, "person")
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["title"] == "People collection"

    response = await request_user_collections(
        client, get_test_token, "anime", page=2, size=1
    )

    assert [entry["reference"] for entry in response.json()["list"]] == [
        public_reference
    ]

    response = await request_user_collections(
        client, get_test_token, "anime", content="unknown-slug"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:bad_content"

    response = await client.get(
        "/collections/me", query_string={"content_type": "anime"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:missing_token"
