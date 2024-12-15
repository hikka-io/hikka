from tests.client_requests import request_client_create, request_client_verify
from starlette import status


async def test_client_verify(client, test_token, test_user, moderator_token):
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

    assert created_client["verified"] == False

    client_reference = created_client["reference"]

    response = await request_client_verify(
        client, moderator_token, client_reference
    )
    assert response.status_code == status.HTTP_200_OK

    assert response.json()["verified"] == True
