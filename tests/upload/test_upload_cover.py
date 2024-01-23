from client_requests import request_upload, request_me
from fastapi import status


async def test_upload_cover(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
):
    response = await request_me(client, get_test_token)
    assert response.json()["cover"] is None

    with open("tests/data/upload/cover.jpg", mode="rb") as file:
        response = await request_upload(client, "cover", get_test_token, file)
        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.json()

        cover_url = response.json()["url"]

        response = await request_me(client, get_test_token)
        assert response.json()["cover"] == cover_url


async def test_upload_cover_bad_permission(
    client,
    create_dummy_user_banned,
    get_dummy_token,
    mock_s3_upload_file,
):
    with open("tests/data/upload/cover.jpg", mode="rb") as file:
        response = await request_upload(client, "cover", get_dummy_token, file)

        # It should fail with permission denied
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["code"] == "permission:denied"


async def test_upload_cover_bad_resolution(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
):
    with open("tests/data/upload/test.jpg", mode="rb") as file:
        response = await request_upload(client, "cover", get_test_token, file)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["code"] == "upload:bad_resolution"


async def test_upload_cover_rate_limit(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
):
    for index in range(0, 11):
        with open("tests/data/upload/cover.jpg", mode="rb") as file:
            response = await request_upload(
                client, "cover", get_test_token, file
            )

            if index != 11:
                continue

            assert response.json()["code"] == "upload:rate_limit"


async def test_upload_cover_rate_limit_admin(
    client,
    create_test_user_moderator,
    get_test_token,
    mock_s3_upload_file,
):
    for index in range(0, 11):
        with open("tests/data/upload/cover.jpg", mode="rb") as file:
            response = await request_upload(
                client, "cover", get_test_token, file
            )

            if index != 11:
                continue

            assert "code" not in response.json()
