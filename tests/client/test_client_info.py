import uuid

from starlette import status

from tests.client_requests import (
    request_client_full_info,
    request_client_create,
    request_client_info,
)


async def test_client_full_info_nonexistent(client, test_token):
    reference = str(uuid.uuid4())

    response = await request_client_full_info(client, test_token, reference)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_client_full_info(client, test_token, test_user):
    name = "test-client"
    description = "test client description"
    endpoint = "hikka://auth/"

    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_200_OK

    client_reference = response.json()["reference"]

    response = await request_client_full_info(
        client, test_token, client_reference
    )
    assert response.status_code == status.HTTP_200_OK

    client_info = response.json()
    assert client_info["name"] == name
    assert client_info["endpoint"] == endpoint
    assert client_info["description"] == description
    assert client_info["user"]["username"] == test_user.username


async def test_client_info_by_reference(client, test_token, test_user):
    name = "test-client"
    description = "test client description"
    endpoint = "hikka://auth/"
    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_200_OK

    client_reference = response.json()["reference"]

    response = await request_client_info(client, client_reference)
    assert response.status_code == status.HTTP_200_OK

    client_info = response.json()
    assert client_info["name"] == name
    assert client_info["description"] == description
    assert client_info["user"]["username"] == test_user.username
