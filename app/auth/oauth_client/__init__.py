# Source: https://github.com/klen/aioauth-client
"""OAuth support for asyncio/trio libraries."""

from __future__ import annotations
from random import SystemRandom
from hashlib import sha1
import logging
import base64
import httpx
import time
import hmac

from urllib.parse import (
    urlencode,
    parse_qsl,
    urlsplit,
    urljoin,
    quote,
)

from typing import (
    Awaitable,
    Generator,
    Optional,
    Union,
    Tuple,
    Type,
    List,
    Dict,
    cast,
    Any,
)


TRes = Union[Dict[str, "TRes"], List["TRes"], str, int, float, bool, None]
THeaders = Dict[str, str]
TParams = Dict[str, str]

RANDOM = SystemRandom().random


class OAuthError(RuntimeError):
    """AIOAuth Exceptions Class."""


class User:
    """Store user's information."""

    __slots__ = (
        "id",
        "email",
        "first_name",
        "last_name",
        "username",
        "picture",
        "link",
        "locale",
        "city",
        "country",
        "gender",
    )

    def __init__(self, **info):
        """Initialize self data."""
        for attr in self.__slots__:
            setattr(self, attr, info.get(attr))


class Signature:
    """Abstract base class for signature methods."""

    name: str = ""

    @staticmethod
    def _escape(s: str) -> str:
        """URL escape a string."""
        return quote(s, safe=b"~")

    def sign(
        self,
        consumer_secret: str,
        method: str,
        url: str,
        oauth_token_secret: Optional[str] = None,
        **params,
    ):
        """Abstract method."""
        raise NotImplementedError("Shouldnt be called.")


class HmacSha1Signature(Signature):
    """HMAC-SHA1 signature-method."""

    name = "HMAC-SHA1"

    def sign(
        self,
        consumer_secret: str,
        method: str,
        url: str,
        oauth_token_secret: Optional[str] = None,
        *,
        escape: bool = False,
        **params,
    ) -> str:
        """Create a signature using HMAC-SHA1."""
        if escape:
            query = [
                (self._escape(k), self._escape(v)) for k, v in params.items()
            ]
            query_string = "&".join(["%s=%s" % item for item in sorted(query)])

        else:
            query_string = urlencode(sorted(params.items()))

        signature = "&".join(
            map(self._escape, (method.upper(), url, query_string))
        )

        key = self._escape(consumer_secret) + "&"
        if oauth_token_secret:
            key += self._escape(oauth_token_secret)

        hashed = hmac.new(key.encode(), signature.encode(), sha1)
        return base64.b64encode(hashed.digest()).decode()


class ClientRegistry(type):
    """Meta class to register OAUTH clients."""

    clients: Dict[str, Type[Client]] = {}

    def __new__(cls, name, bases, params):
        """Save created client in self registry."""
        kls = super().__new__(cls, name, bases, params)
        cls.clients[kls.name] = kls
        return kls


class Client(object, metaclass=ClientRegistry):
    """Base abstract OAuth Client class."""

    name: str = ""
    base_url: str = ""
    user_info_url: str = ""
    access_token_key: str = "access_token"
    shared_key: str = "oauth_verifier"
    access_token_url: str = ""
    authorize_url: str = ""

    def __init__(  # noqa: PLR0913
        self,
        base_url: Optional[str] = None,
        authorize_url: Optional[str] = None,
        access_token_key: Optional[str] = None,
        access_token_url: Optional[str] = None,
        transport: Optional[httpx.AsyncClient] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize the client."""
        self.base_url = base_url or self.base_url
        self.authorize_url = authorize_url or self.authorize_url
        self.access_token_key = access_token_key or self.access_token_key
        self.access_token_url = access_token_url or self.access_token_url
        self.logger = logger or logging.getLogger("OAuth: %s" % self.name)
        self.transport = transport

    def _get_url(self, url: str) -> str:
        """Build provider's url. Join with base_url part if needed."""
        if self.base_url and not url.startswith(("http://", "https://")):
            return urljoin(self.base_url, url)
        return url

    def __str__(self) -> str:
        """String representation."""
        return f"{ self.name.title() } {self.base_url}"

    def __repr__(self):
        """String representation."""
        return f"<{self}>"

    async def _request(
        self,
        method: str,
        url: str,
        *,
        raise_for_status: bool = False,
        **options,
    ) -> TRes:
        """Make a request through HTTPX."""
        transport = self.transport or httpx.AsyncClient()
        async with transport as client:
            self.logger.debug("Request %s: %s", method, url)
            response = await client.request(method, url, **options)
            if raise_for_status and response.status_code >= 300:
                raise OAuthError(str(response))

            if "json" in response.headers.get("CONTENT-TYPE"):
                return response.json()

            return dict(parse_qsl(response.text)) or response.text

    def request(
        self,
        method: str,
        url: str,
        params: Optional[TParams] = None,
        headers: Optional[THeaders] = None,
        **options,
    ) -> Awaitable[TRes]:
        """Make a request to provider."""
        raise NotImplementedError("Shouldnt be called.")

    async def user_info(self, **options) -> Tuple[User, TRes]:
        """Load user information from provider."""
        if not self.user_info_url:
            raise NotImplementedError(
                "The provider doesnt support user_info method."
            )

        data = await self.request(
            "GET",
            self.user_info_url,
            raise_for_status=True,
            **options,
        )
        user = User(**dict(self.user_parse(data)))
        return user, data

    @staticmethod
    def user_parse(_: TRes) -> Generator[Tuple[str, Any], None, None]:
        """Parse user's information from given provider data."""
        yield "id", None

    def get_authorize_url(self, **_) -> str:
        """Get an authorization URL."""
        return self.authorize_url

    async def get_access_token(self, *args, **kwargs) -> Tuple[str, Any]:
        """Abstract base method."""
        raise NotImplementedError


class OAuth1Client(Client):
    """Implement OAuth1."""

    name = "oauth1"
    access_token_key = "oauth_token"
    version = "1.0"
    escape = False
    request_token_url: str = ""

    def __init__(  # noqa: PLR0913
        self,
        consumer_key: str,
        consumer_secret: str,
        base_url: Optional[str] = None,
        authorize_url: Optional[str] = None,
        oauth_token: Optional[str] = None,
        oauth_token_secret: Optional[str] = None,
        request_token_url: Optional[str] = None,
        access_token_url: Optional[str] = None,
        access_token_key: Optional[str] = None,
        transport: Optional[httpx.AsyncClient] = None,
        logger: Optional[logging.Logger] = None,
        signature: Optional[Signature] = None,
        **params,
    ):
        """Initialize the client."""
        super().__init__(
            base_url,
            authorize_url,
            access_token_key,
            access_token_url,
            transport,
            logger,
        )

        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.request_token_url = request_token_url or self.request_token_url
        self.params = params
        self.signature = signature or HmacSha1Signature()

    def get_authorize_url(
        self, request_token: Optional[str] = None, **params
    ) -> str:
        """Return formatted authorization URL."""
        params.update({"oauth_token": request_token or self.oauth_token})
        params.update(self.params)
        return self.authorize_url + "?" + urlencode(params)

    def request(
        self,
        method: str,
        url: str,
        params: Optional[TParams] = None,
        headers: Optional[THeaders] = None,
        **options,
    ) -> Awaitable[TRes]:
        """Make a request to provider."""
        oparams = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_nonce": sha1(str(RANDOM()).encode("ascii")).hexdigest(),
            "oauth_signature_method": self.signature.name,
            "oauth_timestamp": str(int(time.time())),
            "oauth_version": self.version,
        }
        oparams.update(params or {})

        if self.oauth_token:
            oparams["oauth_token"] = self.oauth_token

        url = self._get_url(url)

        if urlsplit(url).query:
            raise ValueError(
                'Request parameters should be in the "params" parameter, not inlined in the URL',  # noqa: E501
            )

        oparams["oauth_signature"] = self.signature.sign(
            self.consumer_secret,
            method,
            url,
            oauth_token_secret=self.oauth_token_secret,
            escape=self.escape,
            **oparams,
        )
        return self._request(
            method, url, params=oparams, headers=headers, **options
        )

    async def get_request_token(self, **params) -> Tuple[str, Any]:
        """Get a request_token and request_token_secret from OAuth1 provider."""
        params = dict(self.params, **params)
        data = await self.request(
            "GET",
            self.request_token_url,
            raise_for_status=True,
            params=params,
        )
        if not isinstance(data, dict):
            return "", data

        self.oauth_token = cast(str, data.get("oauth_token") or "")
        self.oauth_token_secret = cast(str, data.get("oauth_token_secret"))
        return self.oauth_token, data

    async def get_access_token(
        self,
        oauth_verifier,
        request_token=None,
        headers=None,
        **_,
    ) -> Tuple[str, Dict]:
        """Get access_token from OAuth1 provider.

        :returns: (access_token, access_token_secret, provider_data)
        """
        # Possibility to provide REQUEST DATA to the method
        if (
            not isinstance(oauth_verifier, str)
            and self.shared_key in oauth_verifier
        ):
            oauth_verifier = oauth_verifier[self.shared_key]

        if request_token and self.oauth_token != request_token:
            raise OAuthError(
                "Failed to obtain OAuth 1.0 access token. Request token is invalid",  # noqa: E501
            )

        data = await self.request(
            "POST",
            self.access_token_url,
            raise_for_status=True,
            headers=headers,
            params={
                "oauth_verifier": oauth_verifier,
                "oauth_token": request_token,
            },
        )

        if not isinstance(data, dict):
            raise OAuthError(
                f"Failed to obtain OAuth 1.0 access token. Invalid data: {data}",  # noqa: E501
            )

        self.oauth_token = cast(str, data.get("oauth_token") or "")
        self.oauth_token_secret = cast(str, data.get("oauth_token_secret"))

        return self.oauth_token, data


class OAuth2Client(Client):
    """Implement OAuth2."""

    name = "oauth2"
    shared_key = "code"

    def __init__(  # noqa: PLR0913
        self,
        client_id: str,
        client_secret: str,
        base_url: Optional[str] = None,
        authorize_url: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_url: Optional[str] = None,
        access_token_key: Optional[str] = None,
        transport: Optional[httpx.AsyncClient] = None,
        logger: Optional[logging.Logger] = None,
        **params,
    ):
        """Initialize the client."""
        super().__init__(
            base_url,
            authorize_url,
            access_token_key,
            access_token_url,
            transport,
            logger,
        )

        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.params = params

    def get_authorize_url(self, **params) -> str:
        """Return formatted authorize URL."""
        params = dict(self.params, **params)
        params.update({"client_id": self.client_id, "response_type": "code"})
        return f"{ self.authorize_url }?{ urlencode(params) }"

    def request(  # noqa: PLR0913
        self,
        method: str,
        url: str,
        params: Optional[TParams] = None,
        headers: Optional[THeaders] = None,
        access_token: Optional[str] = None,
        **options,
    ) -> Awaitable[TRes]:
        """Request OAuth2 resource."""
        url = self._get_url(url)
        headers = headers or {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        access_token = access_token or self.access_token
        if access_token:
            headers.setdefault("Authorization", "Bearer %s" % access_token)

        return self._request(
            method, url, headers=headers, params=params, **options
        )

    async def get_access_token(
        self,
        code: str,
        redirect_uri: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **payload,
    ) -> Tuple[str, Any]:
        """Get an access_token from OAuth provider.

        :returns: (access_token, provider_data)
        """
        # Possibility to provide REQUEST DATA to the method
        payload.setdefault("grant_type", "authorization_code")
        payload.update(
            {"client_id": self.client_id, "client_secret": self.client_secret},
        )

        if code and not isinstance(code, str) and self.shared_key in code:
            code = code[self.shared_key]
        payload[
            "refresh_token"
            if payload["grant_type"] == "refresh_token"
            else "code"
        ] = code

        redirect_uri = redirect_uri or self.params.get("redirect_uri")
        if redirect_uri:
            payload["redirect_uri"] = redirect_uri

        self.access_token = ""
        data = await self.request(
            "POST",
            self.access_token_url,
            raise_for_status=True,
            data=payload,
            headers=headers,
        )

        if not isinstance(data, dict):
            return "", data

        if "access_token" in data:
            assert isinstance(data["access_token"], str)
            self.access_token = data["access_token"]

        else:
            self.logger.warning(
                "Error when getting the access token.\nData returned by OAuth server: %r",  # noqa: E501
                data,
            )

        return self.access_token or "", data


class DiscordClient(OAuth2Client):
    """Support Discord API.

    * Dashboard: https://discordapp.com/developers/applications/me
    * Docs: https://discordapp.com/developers/docs/topics/oauth2
    * API refer: https://discordapp.com/developers/docs/reference
    """

    access_token_url = "https://discordapp.com/api/oauth2/token"
    authorize_url = "https://discordapp.com/api/oauth2/authorize"
    base_url = "https://discordapp.com/api/v6/"
    name = "discord"
    user_info_url = "https://discordapp.com/api/v6/users/@me"

    @staticmethod
    def user_parse(data: TRes):
        """Parse information from the provider."""
        assert isinstance(data, dict)
        yield "id", data.get("id")
        yield "username", data.get("username")
        yield "discriminator", data.get("discriminator")
        yield "picture", "https://cdn.discordapp.com/avatars/{}/{}.png".format(
            data.get("id"),
            data.get("avatar"),
        )


class TwitterClient(OAuth1Client):
    """Support Twitter.

    * Dashboard: https://dev.twitter.com/apps
    * Docs: https://dev.twitter.com/docs
    * API reference: https://dev.twitter.com/docs/api
    """

    access_token_url = "https://api.twitter.com/oauth/access_token"
    authorize_url = "https://api.twitter.com/oauth/authorize"
    base_url = "https://api.twitter.com/1.1/"
    name = "twitter"
    request_token_url = "https://api.twitter.com/oauth/request_token"
    user_info_url = (
        "https://api.twitter.com/1.1/account/verify_credentials.json"
    )

    @staticmethod
    def user_parse(data):
        """Parse information from the provider."""
        yield "id", data.get("id") or data.get("user_id")
        first_name, _, last_name = data["name"].partition(" ")
        yield "first_name", first_name
        yield "last_name", last_name
        yield "email", data.get("email")
        yield "picture", data.get("profile_image_url")
        yield "locale", data.get("lang")
        yield "link", data.get("url")
        yield "username", data.get("screen_name")
        city, _, country = (
            s.strip() for s in data.get("location", "").partition(",")
        )
        yield "city", city
        yield "country", country


class GoogleClient(OAuth2Client):
    """Support Google.

    * Dashboard: https://console.developers.google.com/project
    * Docs: https://developers.google.com/accounts/docs/OAuth2
    * API reference: https://developers.google.com/gdata/docs/directory
    * API explorer: https://developers.google.com/oauthplayground/
    """

    authorize_url = "https://accounts.google.com/o/oauth2/v2/auth"
    access_token_url = "https://oauth2.googleapis.com/token"
    base_url = "https://www.googleapis.com/userinfo/v2/"
    name = "google"
    user_info_url = "https://www.googleapis.com/userinfo/v2/me"

    @staticmethod
    def user_parse(data):
        """Parse information from provider."""
        yield "id", data.get("id")
        yield "email", data.get("email")
        yield "first_name", data.get("given_name")
        yield "last_name", data.get("family_name")
        yield "link", data.get("link")
        yield "locale", data.get("locale")
        yield "picture", data.get("picture")
        yield "gender", data.get("gender")


# ruff: noqa: S105
