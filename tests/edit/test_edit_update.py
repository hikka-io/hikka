from client_requests import request_create_edit
from client_requests import request_update_edit
from fastapi import status


async def test_edit_update(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # Create edit for anime
    response = await request_create_edit(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        {
            "description": "Brief description",
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    # Check status
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["created"] == response.json()["updated"]

    # Update created edit
    response = await request_update_edit(
        client,
        get_test_token,
        18,
        {
            "description": "Brief description 2",
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == "Brief description 2"
    assert response.json()["created"] != response.json()["updated"]
