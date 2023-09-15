from client_requests import request_create_edit
from client_requests import request_edit
from fastapi import status


async def test_create_edit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    response = await request_create_edit(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        {
            "after": {},
        },
    )

    from pprint import pprint

    pprint(response.json())


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
