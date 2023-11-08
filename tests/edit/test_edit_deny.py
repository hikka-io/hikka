from client_requests import request_create_edit
from client_requests import request_deny_edit
from fastapi import status


async def test_edit_deny(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_moderator,
    create_dummy_user,
    get_test_token,
    get_dummy_token,
    test_session,
):
    # # Create edit for anime
    # response = await request_create_edit(
    #     client,
    #     get_dummy_token,
    #     "anime",
    #     "bocchi-the-rock-9e172d",
    #     {
    #         "description": "Brief description",
    #         "after": {"title_en": "Bocchi The Rock!"},
    #     },
    # )

    # # Check status
    # assert response.status_code == status.HTTP_200_OK

    # # Now make deny request
    # response = await request_deny_edit(client, get_test_token, 1)

    # from pprint import pprint

    # pprint(response.json())

    # assert response.status_code == status.HTTP_200_OK
    pass
