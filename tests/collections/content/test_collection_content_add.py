from client_requests import request_add_collection_content
from client_requests import request_collection_info
from sqlalchemy import select, desc, update
from app.models import Log, Collection
from fastapi import status
from app import constants
from uuid import UUID


def content_orders(response):
    return [
        (entry["content"]["slug"], entry["label"], entry["order"])
        for entry in response.json()["collection"]
    ]


async def test_collection_content_add(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_anime_collection,
    create_test_user,
    get_test_token,
    test_session,
):
    reference = await create_anime_collection(
        get_test_token,
        [
            ("fullmetal-alchemist-brotherhood-fc524a", None),
            ("bocchi-the-rock-9e172d", None),
        ],
    )

    response = await request_add_collection_content(
        client,
        reference,
        get_test_token,
        "kimi-no-na-wa-945779",
        {"comment": "Great movie"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["has_content"] is True
    assert response.json()["content_label"] is None
    assert response.json()["entries"] == 3
    assert response.json()["reference"] == reference

    response = await request_collection_info(client, reference)
    assert response.json()["entries"] == 3
    assert response.json()["collection"][2]["comment"] == "Great movie"
    assert content_orders(response) == [
        ("fullmetal-alchemist-brotherhood-fc524a", None, 1),
        ("bocchi-the-rock-9e172d", None, 2),
        ("kimi-no-na-wa-945779", None, 3),
    ]

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_COLLECTION_UPDATE
    assert log.user == create_test_user
    assert log.target_id == UUID(reference)
    assert set(log.data.keys()) == {"added_content"}
    assert log.data["added_content"]["order"] == 3
    assert log.data["added_content"]["comment"] == "Great movie"


async def test_collection_content_add_groups(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_anime_collection,
    create_test_user,
    get_test_token,
    test_session,
):
    reference = await create_anime_collection(
        get_test_token,
        [
            ("fullmetal-alchemist-brotherhood-fc524a", "Good"),
            ("bocchi-the-rock-9e172d", "Good"),
            ("kimi-no-na-wa-945779", "Great"),
        ],
        ["Good", "Great"],
    )

    # Existing group: inserted after its last entry, later entries shift
    response = await request_add_collection_content(
        client,
        reference,
        get_test_token,
        "oshi-no-ko-421060",
        {"label": "Good"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["content_label"] == "Good"
    assert response.json()["labels_order"] == ["Good", "Great"]

    response = await request_collection_info(client, reference)
    assert content_orders(response) == [
        ("fullmetal-alchemist-brotherhood-fc524a", "Good", 1),
        ("bocchi-the-rock-9e172d", "Good", 2),
        ("oshi-no-ko-421060", "Good", 3),
        ("kimi-no-na-wa-945779", "Great", 4),
    ]

    # New group: appended to labels_order, entry goes to the end
    response = await request_add_collection_content(
        client,
        reference,
        get_test_token,
        "steinsgate-f29797",
        {"label": "Masterpiece"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["labels_order"] == ["Good", "Great", "Masterpiece"]
    assert response.json()["entries"] == 5

    response = await request_collection_info(client, reference)
    assert response.json()["labels_order"] == ["Good", "Great", "Masterpiece"]
    assert content_orders(response)[-1] == (
        "steinsgate-f29797",
        "Masterpiece",
        5,
    )

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.data["old_labels_order"] == ["Good", "Great"]
    assert log.data["labels_order"] == ["Good", "Great", "Masterpiece"]

    # Label is required in a grouped collection
    response = await request_add_collection_content(
        client,
        reference,
        get_test_token,
        "kaguya-sama-wa-kokurasetai-ultra-romantic-fcd761",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:unlabeled_content"


async def test_collection_content_add_bad(
    client,
    aggregator_anime,
    aggregator_anime_info,
    aggregator_people,
    create_anime_collection,
    create_test_user,
    get_test_token,
    test_session,
):
    reference = await create_anime_collection(
        get_test_token,
        [("fullmetal-alchemist-brotherhood-fc524a", None)],
    )

    # Already in collection
    response = await request_add_collection_content(
        client,
        reference,
        get_test_token,
        "fullmetal-alchemist-brotherhood-fc524a",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:content_exists"

    # Unknown slug
    response = await request_add_collection_content(
        client, reference, get_test_token, "unknown-slug"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:bad_content"

    # Slug of another content type
    response = await request_add_collection_content(
        client, reference, get_test_token, "justin-cook-77f1b3"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:bad_content"

    # Label in an ungrouped collection
    response = await request_add_collection_content(
        client,
        reference,
        get_test_token,
        "bocchi-the-rock-9e172d",
        {"label": "Good"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:bad_label"

    # Collection holds at most 500 entries
    await test_session.execute(
        update(Collection)
        .filter(Collection.id == UUID(reference))
        .values(entries=500)
    )
    await test_session.commit()

    response = await request_add_collection_content(
        client,
        reference,
        get_test_token,
        "bocchi-the-rock-9e172d",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:content_limit"

    response = await request_collection_info(client, reference)
    assert len(response.json()["collection"]) == 1
