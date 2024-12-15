import uuid

from starlette import status

from tests.client_requests import (
    request_client_full_info,
    request_client_create,
    request_client_delete,
)


async def test_client_delete(client, test_token):
    name = "test-client"
    description = "test client description"
    endpoint = "hikka://auth/"

    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_200_OK

    client_reference = response.json()["reference"]

    response = await request_client_delete(client, test_token, client_reference)
    assert response.status_code == status.HTTP_200_OK

    response = await request_client_full_info(
        client, test_token, client_reference
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["code"] == "client:not_found"


async def test_client_delete_nonexistent(client, test_token):
    reference = str(uuid.uuid4())
    response = await request_client_delete(client, test_token, reference)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "client:not_found"
