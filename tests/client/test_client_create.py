from starlette import status

from tests.client_requests import request_client_create


async def test_client_create(client, test_token):
    name = "test-client"
    description = "test client description"
    endpoint = "http://localhost/"
    response = await request_client_create(
        client,
        test_token,
        name,
        description,
        endpoint,
    )
    assert response.status_code == status.HTTP_200_OK

    created_client = response.json()

    assert created_client["name"] == name
    assert created_client["description"] == description
    assert created_client["endpoint"] == endpoint
    assert len(created_client["secret"]) == 128


async def test_client_create_invalid_endpoint(client, test_token):
    name = "test-client"
    description = "test client description"
    endpoint = "invalid-endpoint"
    response = await request_client_create(
        client, test_token, name, description, endpoint
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_client_create_double(client, test_token):
    name = "test-client"
    description = "test client description"
    endpoint = "http://localhost/"
    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_200_OK

    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "client:already_exists"
