from .oauth_client import GoogleClient
from app.settings import get_settings

oauth_client_args = {
    "google": {
        "args": {
            "scope": "https://www.googleapis.com/auth/userinfo.email",
            "include_granted_scopes": "true",
            "access_type": "offline",
        },
        "client": GoogleClient,
    },
}


def get_client(provider: str):
    settings = get_settings()

    oauth_provider = settings.oauth.get(provider)
    client_class = oauth_client_args[provider]["client"]  # type: ignore

    return client_class(
        **{
            "client_secret": oauth_provider["client_secret"],
            "client_id": oauth_provider["client_id"],
        }
    )


async def get_url(provider: str) -> dict[str, str]:
    client = get_client(provider)

    settings = get_settings()
    oauth_provider = settings.oauth.get(provider)

    url = client.get_authorize_url(
        **{
            "redirect_uri": oauth_provider["redirect_uri"],
            **oauth_client_args[provider]["args"],
            # "state": "hikka",  # ToDo: generate state server side
        }
    )

    return {"url": url}
