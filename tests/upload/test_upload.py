from client_requests import request_upload
from fastapi import status


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
            response = await request_upload(
                client, "avatar", get_test_token, file
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["code"] == "upload:bad_mime"


async def test_upload_bad_size(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
):
    with open("tests/data/upload/test_bad_size.jpg", mode="rb") as file:
        response = await request_upload(client, "avatar", get_test_token, file)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["code"] == "upload:bad_size"
