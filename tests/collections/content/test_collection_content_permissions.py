from client_requests import request_delete_collection_content
from client_requests import request_add_collection_content
from client_requests import request_collection_info
from fastapi import status
from app import constants


async def test_collection_content_permissions(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_anime_collection,
    create_dummy_user,
    create_test_user_moderator,
    get_dummy_token,
    get_test_token,
):
    reference = await create_anime_collection(
        get_dummy_token,
        [
            ("fullmetal-alchemist-brotherhood-fc524a", None),
            ("bocchi-the-rock-9e172d", None),
        ],
    )

    private_reference = await create_anime_collection(
        get_dummy_token,
        [
            ("fullmetal-alchemist-brotherhood-fc524a", None),
            ("bocchi-the-rock-9e172d", None),
        ],
        visibility=constants.COLLECTION_PRIVATE,
    )

    # Moderators can't change content of other users' collections
    response = await request_add_collection_content(
        client, reference, get_test_token, "kimi-no-na-wa-945779"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"

    response = await request_delete_collection_content(
        client, reference, get_test_token, "bocchi-the-rock-9e172d"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"

    response = await request_add_collection_content(
        client,
        private_reference,
        get_test_token,
        "kimi-no-na-wa-945779",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = await client.put(
        f"/collections/{reference}/content/kimi-no-na-wa-945779", json={}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:missing_token"

    response = await request_collection_info(client, reference)
    assert response.json()["entries"] == 2
    assert len(response.json()["collection"]) == 2
