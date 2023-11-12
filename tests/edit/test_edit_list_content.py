from client_requests import request_content_edit_list
from client_requests import request_create_edit
from fastapi import status


async def test_edit_list_content(
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

    # Get list of Bocchi edits
    response = await request_content_edit_list(
        client, "anime", "bocchi-the-rock-9e172d"
    )

    # Check status and data
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1

    assert response.json()["list"][0]["after"]["title_en"] == "Bocchi The Rock!"
    assert response.json()["list"][0]["description"] == "Brief description"
    assert response.json()["list"][0]["author"]["username"] == "username"
    assert response.json()["list"][0]["content_type"] == "anime"
    assert response.json()["list"][0]["status"] == "pending"
    assert response.json()["list"][0]["moderator"] is None
    assert response.json()["list"][0]["before"] is None
    assert response.json()["list"][0]["edit_id"] == 1
