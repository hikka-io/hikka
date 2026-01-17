from starlette import status

from tests.client_requests import request_client_create
from app import constants


async def test_client_create(client, test_token, test_user):
    name = "test-client"
    description = "test client description"
    endpoint = "hikka://auth/"
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
    assert created_client["endpoint"] == endpoint
    assert created_client["description"] == description
    assert created_client["user"]["username"] == test_user.username

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
    endpoint = "hikka://auth/"
    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_200_OK

    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "client:already_exists"


async def test_too_long_fields(client, test_token):
    error_message_format = "Invalid field {field} in request body"
    error_code = "system:validation_error"

    response = await request_client_create(
        client,
        test_token,
        "a" * (constants.MAX_CLIENT_NAME_LENGTH + 1),
        "description",
        "hikka://auth/",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == error_code
    assert response.json()["message"] == error_message_format.format(
        field="name"
    )

    response = await request_client_create(
        client,
        test_token,
        "name",
        "a" * (constants.MAX_CLIENT_DESCRIPTION_LENGTH + 1),
        "hikka://auth/",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == error_code
    assert response.json()["message"] == error_message_format.format(
        field="description"
    )

    response = await request_client_create(
        client,
        test_token,
        "name",
        "description",
        "hikka://auth/" + "a" * (constants.MAX_CLIENT_ENDPOINT_LENGTH + 1),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == error_code
    assert response.json()["message"] == error_message_format.format(
        field="endpoint"
    )


async def test_too_short_fields(client, test_token):
    error_message_format = "Invalid field {field} in request body"
    error_code = "system:validation_error"

    response = await request_client_create(
        client,
        test_token,
        "a",
        "description",
        "hikka://auth/",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["code"] == error_code
    assert response.json()["message"] == error_message_format.format(
        field="name"
    )

    response = await request_client_create(
        client,
        test_token,
        "name",
        "a",
        "hikka://auth/",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["code"] == error_code
    assert response.json()["message"] == error_message_format.format(
        field="description"
    )
