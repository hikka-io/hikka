from pydantic import AnyUrl, Field, field_validator

from app.schemas import CustomModel, ClientResponse, PaginationResponse
from app import constants, utils


class ClientFullResponse(ClientResponse):
    secret: str
    endpoint: str


class ClientPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[ClientResponse]


class ClientCreate(CustomModel):
    name: str = Field(
        examples=["ThirdPartyWatchlistImporter"],
        description="Client name",
        min_length=3,
        max_length=constants.MAX_CLIENT_NAME_LENGTH,
    )
    description: str = Field(
        examples=["Client that imports watchlist from third-party services"],
        description="Short clear description of the client",
        min_length=3,
        max_length=constants.MAX_CLIENT_DESCRIPTION_LENGTH,
    )
    endpoint: AnyUrl = Field(
        examples=["https://example.com", "http://localhost/auth/confirm", "hikka://auth"],
        description="Endpoint of the client. "
        "User will be redirected to that endpoint after successful "
        "authorization",
        max_length=constants.MAX_CLIENT_ENDPOINT_LENGTH,
    )

    @field_validator("name", "description", mode="before")
    def validate_name(cls, v: str) -> str:
        if not isinstance(v, str):
            return v

        return utils.remove_bad_characters(v).strip()

    @field_validator("endpoint")
    def validate_endpoint(cls, v: AnyUrl) -> AnyUrl:
        if len(str(v)) > constants.MAX_CLIENT_ENDPOINT_LENGTH:
            raise ValueError(
                f"Endpoint length should be less than {constants.MAX_CLIENT_ENDPOINT_LENGTH}"
            )

        return v


class ClientUpdate(CustomModel):
    name: str | None = Field(
        None,
        description="Client name",
        max_length=constants.MAX_CLIENT_NAME_LENGTH,
        min_length=3,
    )
    description: str | None = Field(
        None,
        description="Short clear description of the client",
        max_length=constants.MAX_CLIENT_DESCRIPTION_LENGTH,
        min_length=3,
    )
    endpoint: AnyUrl | None = Field(
        None,
        description="Endpoint of the client",
        max_length=constants.MAX_CLIENT_ENDPOINT_LENGTH,
    )
    revoke_secret: bool = Field(
        False,
        description="Create new client secret and revoke previous",
    )

    @field_validator("name", "description", mode="before")
    def validate_name(cls, v: str) -> str:
        if not isinstance(v, str):
            return v

        return utils.remove_bad_characters(v).strip()

    @field_validator("endpoint")
    def validate_endpoint(cls, v: AnyUrl | None) -> AnyUrl | None:
        if len(str(v)) > constants.MAX_CLIENT_ENDPOINT_LENGTH:
            raise ValueError(
                f"Endpoint length should be less than {constants.MAX_CLIENT_ENDPOINT_LENGTH}"
            )

        return v


class ListAllClientsArgs(CustomModel):
    query: str | None = Field(None, description="Search by name")
