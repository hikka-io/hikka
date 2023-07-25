from .oauth_client import GoogleClient, OAuthError
from .constants import oauth_url_args
from app.settings import get_settings
from app.errors import Abort


def get_client_class(provider: str):
    provider_classes = {
        "google": GoogleClient,
    }

    return provider_classes.get(provider)


def get_client(provider: str):
    settings = get_settings()

    if not (oauth_provider := settings.oauth[provider]):
        raise Abort("auth", "invalid-provider")

    client_class = get_client_class(provider)

    return client_class(**oauth_provider)


async def get_url(provider: str) -> dict[str, str]:
    client = get_client(provider)

    return {
        "url": client.get_authorize_url(**oauth_url_args[provider]),
    }


async def get_info(provider: str, code: str):
    client = get_client(provider)
    data = None

    try:
        otoken, _ = await client.get_access_token(
            code, oauth_url_args[provider]["redirect_uri"]
        )

        client.access_token = otoken
        _, data = await client.user_info()

    except OAuthError:
        raise Abort("auth", "invalid-token")

    return data
