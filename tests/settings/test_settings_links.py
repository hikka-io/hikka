from client_requests import request_settings_links
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_settings_links_bad(client, create_test_user, get_test_token):
    # Change links for user
    response = await request_settings_links(
        client,
        get_test_token,
        [
            {
                "url": "https://link.com",
                "icon": "custom",
            }
        ],
    )

    # Now check if user links has been upated
    assert response.status_code == status.HTTP_200_OK


# async def test_settings_links(
#     client, create_test_user, get_test_token, test_session
# ):
#     # Change links for user
#     response = await request_settings_links(
#         client,
#         get_test_token,
#         [
#             {
#                 "text": f"Link {index}",
#                 "url": f"https://link{index}.com",
#                 "icon": "custom",
#             }
#             for index in range(1, 10)
#         ],
#     )

#     # Now check if user links has been upated
#     assert response.status_code == status.HTTP_200_OK
#     # assert response.json()["username"] == "new_username"

#     # # Change username again
#     # response = await request_settings_username(
#     #     client, get_test_token, "new_username_2"
#     # )

#     # # It should hit rate limit
#     # assert response.status_code == status.HTTP_400_BAD_REQUEST
#     # assert response.json()["code"] == "settings:username_cooldown"

#     # # Check log
#     # log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
#     # assert log.log_type == constants.LOG_SETTINGS_USERNAME
#     # assert log.user == create_test_user
#     # assert log.data["before"] == "testuser"
#     # assert log.data["after"] == "new_username"
