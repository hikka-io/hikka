import uuid

from starlette import status

from tests.client_requests import (
    request_client_full_info,
    request_client_create,
    request_client_delete,
    request_me,
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


async def test_client_delete_admin(
    client,
    test_thirdparty_client,
    test_thirdparty_token,
    test_token,
    moderator_token,
    admin_token,
):
    reference = test_thirdparty_client.reference

    # Other users can't delete client
    response = await request_client_delete(client, moderator_token, reference)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "client:not_owner"

    # But admins can
    response = await request_client_delete(client, admin_token, reference)
    assert response.status_code == status.HTTP_200_OK

    response = await request_client_full_info(client, test_token, reference)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "client:not_found"

    # Tokens issued for deleted client expire
    response = await request_me(client, test_thirdparty_token)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "auth:token_expired"
