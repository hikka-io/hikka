from httpx import AsyncClient

from app.auth.oauth_client import (
    HmacSha1Signature,
    GoogleClient,
    UserData,
)


def test_userinfo():
    user = UserData(email="email")
    assert user.email == "email"
    assert user.id is None


def test_signatures():
    sig = HmacSha1Signature()
    assert sig.name
    assert sig.sign("secret", "GET", "/test", oauth_token_secret="secret")


async def test_client(oauth_http):
    google = GoogleClient(
        client_id="cid",
        client_secret="secret",
        access_token="token",
    )

    data = await google.request("GET", "/")
    assert data == {
        "email": "user@mail.com",
        "response": "ok",
        "id": "test-id",
    }

    oauth_http.assert_called_with(
        "GET",
        "https://www.googleapis.com/",
        params=None,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Authorization": "Bearer token",
        },
    )


async def test_custom_client(oauth_http, oauth_response):
    transport = AsyncClient()

    google = GoogleClient(
        client_id="cid",
        client_secret="secret",
        access_token="token",
        transport=transport,
    )

    assert google.transport

    oauth_http.return_value = oauth_response(json={"access_token": "TOKEN"})
    token, meta = await google.get_access_token("000")

    assert oauth_http.called
    assert meta
    assert token
