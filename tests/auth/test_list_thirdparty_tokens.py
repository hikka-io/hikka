from starlette import status

from tests.client_requests import (
    request_list_thirdparty_tokens,
    request_auth_token_info,
)


async def test_list_no_thirdparty_tokens(client, test_token):
    response = await request_list_thirdparty_tokens(client, test_token)
    assert response.status_code == status.HTTP_200_OK

    assert response.json()["list"] == []
    assert response.json()["pagination"] == {"total": 0, "page": 1, "pages": 0}


async def test_list_thirdparty_tokens(
    client, test_token, test_thirdparty_token
):
    response = await request_auth_token_info(client, test_thirdparty_token)
    assert response.status_code == status.HTTP_200_OK

    token_info = response.json()

    response = await request_list_thirdparty_tokens(client, test_token)
    assert response.status_code == status.HTTP_200_OK

    assert response.json()["pagination"] == {"total": 1, "page": 1, "pages": 1}

    assert response.json()["list"] == [token_info]
