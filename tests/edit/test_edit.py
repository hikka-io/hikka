from client_requests import request_create_edit
from client_requests import request_edit
from sqlalchemy import select
from fastapi import status
from app import constants

from app.models import (
    PersonContentEdit,
    AnimeContentEdit,
    ContentEdit,
)


async def test_create_edit(
    client,
    aggregator_people,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    pass


# # Let's check if we can get edit by numeric id
# response = await request_edit(client, 1)

# assert response.status_code == status.HTTP_200_OK
# assert isinstance(response.json()["created"], int)

# assert response.json()["after"]["title_en"] == "Bocchi The Rock!"
# assert response.json()["description"] == "Brief description"
# assert response.json()["author"]["username"] == "username"
# assert response.json()["content_type"] == "anime"
# assert response.json()["status"] == "pending"
# assert response.json()["moderator"] is None
# assert response.json()["before"] is None
# assert response.json()["edit_id"] == 1


# ToDo: tests for bad permissions
# ToDo: test for creating edit
# ToDo: test for getting list of edits
# ToDo: test for getting edit info
# ToDo: test for updating the edit
# ToDo: test for approving the edit
# ToDo: test for denying the edit


# async def test_edit(client):
#     # Try to fetch unknown edit
#     response = await request_edit(client, 1)

#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     assert response.json()["code"] == "edit:not_found"
