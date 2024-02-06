from client_requests import request_upload, request_me
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_upload_avatar(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
    test_session,
):
    with open("tests/data/upload/test.jpg", mode="rb") as file:
        response = await request_upload(client, "avatar", get_test_token, file)
        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.json()

        avatar_url = response.json()["url"]

        response = await request_me(client, get_test_token)
        assert response.json()["avatar"] == avatar_url

        # Check avatar upload log
        log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
        assert log.log_type == constants.LOG_UPLOAD
        assert log.user == create_test_user
        assert log.data["upload_type"] == "avatar"


async def test_upload_avatar_bad_permission(
    client,
    create_dummy_user_banned,
    get_dummy_token,
    mock_s3_upload_file,
):
    with open("tests/data/upload/test.jpg", mode="rb") as file:
        response = await request_upload(client, "avatar", get_dummy_token, file)

        # It should fail with permission denied
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["code"] == "permission:denied"


async def test_upload_avatar_bad_resolution(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
):
    images = [
        "tests/data/upload/test_2000x2000.jpg",
        "tests/data/upload/test_100x100.jpg",
    ]

    for image_path in images:
        with open(image_path, mode="rb") as file:
            response = await request_upload(
                client, "avatar", get_test_token, file
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["code"] == "upload:bad_resolution"


async def test_upload_avatar_not_square(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
):
    with open("tests/data/upload/test_not_square.jpg", mode="rb") as file:
        response = await request_upload(client, "avatar", get_test_token, file)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["code"] == "upload:not_square"


async def test_upload_avatar_rate_limit(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
):
    for index in range(0, 11):
        with open("tests/data/upload/test.jpg", mode="rb") as file:
            response = await request_upload(
                client, "avatar", get_test_token, file
            )

            if index != 11:
                continue

            assert response.json()["code"] == "upload:rate_limit"


async def test_upload_avatar_rate_limit_admin(
    client,
    create_test_user_moderator,
    get_test_token,
    mock_s3_upload_file,
):
    for index in range(0, 11):
        with open("tests/data/upload/test.jpg", mode="rb") as file:
            response = await request_upload(
                client, "avatar", get_test_token, file
            )

            if index != 11:
                continue

            assert "code" not in response.json()
