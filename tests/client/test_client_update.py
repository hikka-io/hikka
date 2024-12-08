import uuid

from starlette import status

from tests.client_requests import request_client_create, request_client_update
from app import constants


async def test_client_update(client, test_token):
    name = "test-client"
    description = "test client description"
    endpoint = "hikka://auth/"

    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_200_OK

    old_client_info = response.json()
    assert old_client_info["name"] == name
    assert old_client_info["description"] == description
    assert old_client_info["endpoint"] == endpoint

    new_name = "test-client-updated"
    new_description = "test client description updated"
    new_endpoint = "http://localhost/updated"

    response = await request_client_update(
        client,
        test_token,
        old_client_info["reference"],
        new_name,
        new_description,
        new_endpoint,
        revoke_secret=True,
    )
    assert response.status_code == status.HTTP_200_OK

    new_client_info = response.json()
    assert new_client_info["name"] == new_name
    assert new_client_info["description"] == new_description
    assert new_client_info["endpoint"] == new_endpoint

    assert new_client_info["secret"] != old_client_info["secret"]


async def test_client_update_nonexistent(client, test_token):
    reference = str(uuid.uuid4())

    response = await request_client_update(
        client, test_token, reference, revoke_secret=True
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["code"] == "client:not_found"


async def test_too_long_fields(client, test_token):
    error_message_format = "Invalid field {field} in request body"
    error_code = "system:validation_error"

    name = "test-client"
    description = "test client description"
    endpoint = "hikka://auth/"

    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_200_OK

    client_reference = response.json()["reference"]

    response = await request_client_update(
        client,
        test_token,
        client_reference,
        name="a" * (constants.MAX_CLIENT_NAME_LENGTH + 1),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == error_code
    assert response.json()["message"] == error_message_format.format(
        field="name"
    )

    response = await request_client_update(
        client,
        test_token,
        client_reference,
        description="a" * (constants.MAX_CLIENT_DESCRIPTION_LENGTH + 1),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == error_code
    assert response.json()["message"] == error_message_format.format(
        field="description"
    )

    response = await request_client_update(
        client,
        test_token,
        client_reference,
        endpoint="hikka://auth/"
        + "a" * (constants.MAX_CLIENT_ENDPOINT_LENGTH + 1),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == error_code
    assert response.json()["message"] == error_message_format.format(
        field="endpoint"
    )


async def test_too_short_fields(client, test_token):
    error_message_format = "Invalid field {field} in request body"
    error_code = "system:validation_error"

    name = "test-client"
    description = "test client description"
    endpoint = "hikka://auth/"

    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_200_OK

    client_reference = response.json()["reference"]

    response = await request_client_update(
        client, test_token, client_reference, name="a"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["code"] == error_code
    assert response.json()["message"] == error_message_format.format(
        field="name"
    )

    response = await request_client_update(
        client, test_token, client_reference, description="a"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["code"] == error_code
    assert response.json()["message"] == error_message_format.format(
        field="description"
    )
