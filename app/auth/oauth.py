# ToDo: this file needs major cleanup

from .oauth_client import GoogleClient, OAuthError
from app.settings import get_settings
from app.errors import Abort

oauth_client_args = {
    "google": {
        "scope": "https://www.googleapis.com/auth/userinfo.email",
        "include_granted_scopes": "true",
        "access_type": "offline",
    }
}


def get_client_class(provider: str):
    provider_classes = {
        "google": GoogleClient,
    }

    return provider_classes.get(provider)


def get_client(provider: str):
    settings = get_settings()

    # ToDo: remove this (?) since we already have validate_provider decorator
    if not (oauth_provider := settings.oauth.get(provider)):
        raise Abort("auth", "invalid-provider")

    client_class = get_client_class(provider)

    return client_class(**oauth_provider)


async def get_url(provider: str) -> dict[str, str]:
    client = get_client(provider)

    settings = get_settings()
    oauth_provider = settings.oauth.get(provider)

    # ToDo: make this look less awful
    return {
        "url": client.get_authorize_url(
            **{
                "redirect_uri": oauth_provider["redirect_uri"],
                "scope": oauth_client_args[provider]["scope"],
                "include_granted_scopes": oauth_client_args[provider][
                    "include_granted_scopes"
                ],
                "access_type": oauth_client_args[provider]["access_type"],
                # "state": "hikka",  # ToDo: generate state server side
            }
        ),
    }


async def get_info(provider: str, code: str):
    client = get_client(provider)
    data = None

    settings = get_settings()
    oauth_provider = settings.oauth.get(provider)

    try:
        otoken, _ = await client.get_access_token(
            code, oauth_provider["redirect_uri"]
        )

        client.access_token = otoken
        _, data = await client.user_info()

    except OAuthError:
        raise Abort("auth", "invalid-token")

    return data
