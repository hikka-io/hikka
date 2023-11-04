from client_requests import request_create_edit
from client_requests import request_edit
from fastapi import status


async def test_edit(
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

    # Check status and data
    assert response.status_code == status.HTTP_200_OK

    # Let's check if we can get edit by numeric id
    response = await request_edit(client, 1)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json()["created"], int)

    assert response.json()["after"]["title_en"] == "Bocchi The Rock!"
    assert response.json()["description"] == "Brief description"
    assert response.json()["author"]["username"] == "username"
    assert response.json()["content_type"] == "anime"
    assert response.json()["status"] == "pending"
    assert response.json()["moderator"] is None
    assert response.json()["before"] is None
    assert response.json()["edit_id"] == 1


# ToDo: tests for bad permissions
# ToDo: test for getting list of edits
# ToDo: test for updating the edit
# ToDo: test for approving the edit
# ToDo: test for denying the edit
