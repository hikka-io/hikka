from client_requests import request_content_edit_list
from client_requests import request_create_edit
from fastapi import status


async def test_edit_bad_permission_create(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    create_dummy_user_banned,
    get_test_token,
    get_dummy_token,
    test_session,
):
    # Create edit for anime
    response = await request_create_edit(
        client,
        get_dummy_token,
        "anime",
        "bocchi-the-rock-9e172d",
        {
            "description": "Brief description",
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    # Check status
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"


# async def test_edit_bad_permission_approve(
#     client,
#     aggregator_anime,
#     aggregator_anime_info,
#     create_test_user,
#     create_dummy_user_banned,
#     get_test_token,
#     get_dummy_token,
#     test_session,
# ):
#     # Create edit for anime
#     response = await request_create_edit(
#         client,
#         get_dummy_token,
#         "anime",
#         "bocchi-the-rock-9e172d",
#         {
#             "description": "Brief description",
#             "after": {"title_en": "Bocchi The Rock!"},
#         },
#     )

#     # Check status
#     assert response.status_code == status.HTTP_403_FORBIDDEN
#     assert response.json()["code"] == "permission:denied"
