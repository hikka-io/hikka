import pytest


async def test_create_user(client):
    response = await client.post(
        "/auth/signup",
        json={
            "username": "test_user",
            "password": "password",
            "email": "test@mail.com",
        },
    )

    print(response.json())

    assert response.status_code == 200
