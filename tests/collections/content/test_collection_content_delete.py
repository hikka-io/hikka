from client_requests import request_delete_collection_content
from client_requests import request_collection_info
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants
from uuid import UUID


def content_orders(response):
    return [
        (entry["content"]["slug"], entry["label"], entry["order"])
        for entry in response.json()["collection"]
    ]


async def test_collection_content_delete(
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
            ("bocchi-the-rock-9e172d", "Great"),
            ("kimi-no-na-wa-945779", "Good"),
            ("oshi-no-ko-421060", "Great"),
        ],
        ["Good", "Great"],
    )

    response = await request_delete_collection_content(
        client, reference, get_test_token, "bocchi-the-rock-9e172d"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["has_content"] is False
    assert response.json()["content_label"] is None
    assert response.json()["entries"] == 3
    assert response.json()["labels_order"] == ["Good", "Great"]

    response = await request_collection_info(client, reference)
    assert response.json()["entries"] == 3
    assert content_orders(response) == [
        ("fullmetal-alchemist-brotherhood-fc524a", "Good", 1),
        ("kimi-no-na-wa-945779", "Good", 2),
        ("oshi-no-ko-421060", "Great", 3),
    ]

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_COLLECTION_UPDATE
    assert log.user == create_test_user
    assert log.target_id == UUID(reference)
    assert set(log.data.keys()) == {"deleted_content"}
    assert log.data["deleted_content"]["label"] == "Great"
    assert log.data["deleted_content"]["order"] == 2

    # Removing the last entry of a group drops the group
    response = await request_delete_collection_content(
        client, reference, get_test_token, "oshi-no-ko-421060"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["labels_order"] == ["Good"]

    response = await request_collection_info(client, reference)
    assert response.json()["labels_order"] == ["Good"]
    assert content_orders(response) == [
        ("fullmetal-alchemist-brotherhood-fc524a", "Good", 1),
        ("kimi-no-na-wa-945779", "Good", 2),
    ]

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.data["old_labels_order"] == ["Good", "Great"]
    assert log.data["labels_order"] == ["Good"]

    response = await request_delete_collection_content(
        client,
        reference,
        get_test_token,
        "fullmetal-alchemist-brotherhood-fc524a",
    )

    assert response.status_code == status.HTTP_200_OK

    # Collection must keep at least one entry
    response = await request_delete_collection_content(
        client, reference, get_test_token, "kimi-no-na-wa-945779"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:content_limit"

    response = await request_collection_info(client, reference)
    assert content_orders(response) == [("kimi-no-na-wa-945779", "Good", 1)]


async def test_collection_content_delete_not_found(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_anime_collection,
    create_test_user,
    get_test_token,
):
    reference = await create_anime_collection(
        get_test_token,
        [
            ("fullmetal-alchemist-brotherhood-fc524a", None),
            ("bocchi-the-rock-9e172d", None),
        ],
    )

    for slug in ["kimi-no-na-wa-945779", "unknown-slug"]:
        response = await request_delete_collection_content(
            client, reference, get_test_token, slug
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["code"] == "collections:content_not_found"
