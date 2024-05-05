from app.utils import get_settings
from urllib.parse import urlencode
import aiohttp


# Config data for specific oauth services
# For now only Google :)
providers = {
    "google": {
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "user_info_url": "https://www.googleapis.com/userinfo/v2/me",
        "access_token_url": "https://oauth2.googleapis.com/token",
        "args": {
            "scope": "https://www.googleapis.com/auth/userinfo.email",
            "include_granted_scopes": "true",
            "access_type": "offline",
            "response_type": "code",
        },
    },
}


async def request_access_token(
    access_token_url: str,
    redirect_uri: str,
    client_id: str,
    client_secret: str,
    code: str,
) -> str | None:
    """Request access token from oauth provider service"""

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                access_token_url,
                data={
                    # NOTE: is grant_type Google specific?
                    "grant_type": "authorization_code",
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "client_id": client_id,
                    "code": code,
                },
            ) as result:
                data = await result.json()

                if "access_token" not in data:
                    return None

                return data["access_token"]

    except aiohttp.ClientError:
        return None


async def request_user_data(
    user_info_url: str, access_token: str
) -> dict | None:
    """Request user data from oauth provider service"""

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                user_info_url,
                headers={"Authorization": f"Bearer {access_token}"},
            ) as result:
                return await result.text()

    except aiohttp.ClientError:
        return None


def build_authorize_url(
    redirect_uri: str, client_id: str, authorize_url: str, args: dict
) -> str:
    """This function builds oauth url"""

    params = {
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        **args,
    }

    return f"{authorize_url}?{urlencode(params)}"


async def get_url(provider: str) -> dict[str, str]:
    settings = get_settings()

    provider_settings = settings.oauth.get(provider)
    provider_data = providers[provider]

    url = build_authorize_url(
        provider_settings["redirect_uri"],
        provider_settings["client_id"],
        provider_data["authorize_url"],
        provider_data["args"],
    )

    return {"url": url}


async def get_user_data(provider: str, code: str) -> dict | None:
    settings = get_settings()

    provider_settings = settings.oauth.get(provider)
    provider_data = providers[provider]

    if not (
        access_token := await request_access_token(
            provider_data["access_token_url"],
            provider_settings["redirect_uri"],
            provider_settings["client_id"],
            provider_settings["client_secret"],
            code,
        )
    ):
        return None

    if not (
        data := await request_user_data(
            provider_data["user_info_url"], access_token
        )
    ):
        return None

    return data
