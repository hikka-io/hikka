from fastapi import status

from client_requests import (
    request_upload_avatar,
    request_me,
)

# ToDo: rate limit


async def test_upload(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
):
    with open("tests/data/upload/test.jpg", mode="rb") as file:
        response = await request_upload_avatar(client, get_test_token, file)
        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.json()

        avatar_url = response.json()["url"]

        response = await request_me(client, get_test_token)
        assert response.json()["avatar"] == avatar_url


async def test_upload_bad_mime(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
):
    images = [
        "tests/data/upload/bad_image.jpg",
        "tests/data/upload/test_fake.jpg",
        "tests/data/upload/test.png",
    ]

    for image_path in images:
        with open(image_path, mode="rb") as file:
            response = await request_upload_avatar(client, get_test_token, file)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["code"] == "upload:bad_mime"


async def test_upload_bad_resolution(
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
            response = await request_upload_avatar(client, get_test_token, file)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["code"] == "upload:bad_resolution"


async def test_upload_bad_size(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
):
    with open("tests/data/upload/test_bad_size.jpg", mode="rb") as file:
        response = await request_upload_avatar(client, get_test_token, file)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["code"] == "upload:bad_size"


async def test_upload_not_square(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
):
    with open("tests/data/upload/test_not_square.jpg", mode="rb") as file:
        response = await request_upload_avatar(client, get_test_token, file)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["code"] == "upload:not_square"
