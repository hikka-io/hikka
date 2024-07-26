from pydantic import Field, HttpUrl

from app.schemas import CustomModel, ClientResponse


class ClientFullResponse(ClientResponse):
    secret: str
    endpoint: str


class ClientCreate(CustomModel):
    name: str = Field(
        examples=["ThirdPartyWatchlistImporter"], description="Client name"
    )
    description: str = Field(
        examples=["Client that imports watchlist from third-party services"],
        description="Short clear description of the client",
    )
    endpoint: HttpUrl = Field(
        examples=["https://example.com", "http://localhost/auth/confirm"],
        description="Endpoint of the client. "
        "User will be redirected to that endpoint after successful "
        "authorization",
    )


class ClientUpdate(CustomModel):
    name: str | None = Field(
        None,
        description="Client name",
    )
    description: str | None = Field(
        None,
        description="Short clear description of the client",
    )
    endpoint: HttpUrl | None = Field(None, description="Endpoint of the client")
    revoke_secret: bool = Field(
        False,
        description="Create new client secret and revoke previous",
    )
