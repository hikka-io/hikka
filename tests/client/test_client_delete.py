from starlette import status

from tests.client_requests import (
    request_my_client_info,
    request_client_create,
    request_client_delete,
)


async def test_client_delete(client, test_token):
    name = "test-client"
    description = "test client description"
    endpoint = "http://localhost/"

    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_200_OK

    response = await request_client_delete(client, test_token)
    assert response.status_code == status.HTTP_200_OK

    response = await request_my_client_info(client, test_token)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["code"] == "client:not_found"


async def test_client_delete_nonexistent(client, test_token):
    response = await request_client_delete(client, test_token)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "client:not_found"
