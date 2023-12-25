from fastapi import status

from client_requests import (
    request_upload_avatar,
    request_me,
)

# ToDo: bad mime
# ToDo: bad resolution
# ToDo: bad size
# ToDo: rate limit


async def test_upload(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
):
    with open("tests/data/test.jpg", mode="rb") as file:
        response = await request_upload_avatar(client, get_test_token, file)
        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.json()

        avatar_url = response.json()["url"]

        response = await request_me(client, get_test_token)
        assert response.json()["avatar"] == avatar_url
