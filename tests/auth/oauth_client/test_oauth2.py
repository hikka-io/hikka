from app.auth.oauth_client import GoogleClient, ClientRegistry


async def test_oauth2(oauth_http, oauth_response):
    google = GoogleClient(
        client_id="cid",
        client_secret="secret",
        access_token="token",
    )

    assert google
    assert "google" in ClientRegistry.clients

    assert (
        google.get_authorize_url()
        == "https://accounts.google.com/o/oauth2/v2/auth?client_id=cid&response_type=code"
    )

    oauth_http.return_value = oauth_response(
        json={"access_token": "TEST-TOKEN"}
    )

    token, meta = await google.get_access_token("000")

    assert token == "TEST-TOKEN"
    assert meta
    assert oauth_http.called

    oauth_http.reset_mock()
    oauth_http.return_value = oauth_response(
        json={"access_token": "TEST-TOKEN"}
    )

    res = await google.request("GET", "user", access_token="NEW-TEST-TOKEN")
    assert res

    oauth_http.assert_called_with(
        "GET",
        "https://www.googleapis.com/userinfo/v2/user",
        params=None,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Authorization": "Bearer NEW-TEST-TOKEN",
        },
    )


async def test_oauth2_request(oauth_http):
    google = GoogleClient(
        client_id="cid", client_secret="csecret", access_token="token"
    )

    res = await google.request("GET", "/user", params={"test": "ok"})
    assert res

    oauth_http.assert_called_with(
        "GET",
        "https://www.googleapis.com/user",
        params={"test": "ok"},
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Authorization": "Bearer token",
        },
    )
