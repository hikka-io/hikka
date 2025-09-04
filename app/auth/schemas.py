from app.schemas import datetime_pd, ClientResponse, PaginationResponse
from pydantic import Field
from app import constants
import uuid

from app.schemas import (
    UsernameArgs,
    PasswordArgs,
    CustomModel,
    EmailArgs,
    TokenArgs,
)


# Args
class SignupArgs(UsernameArgs, PasswordArgs, EmailArgs):
    pass


class EmailLoginArgs(PasswordArgs, EmailArgs): ...


class UsernameLoginArgs(PasswordArgs, UsernameArgs): ...


class ComfirmResetArgs(PasswordArgs, TokenArgs):
    pass


class CodeArgs(CustomModel):
    code: str


# Responses
class ProviderUrlResponse(CustomModel):
    url: str = Field(examples=["https://accounts.google.com/o/oauth2/v2/auth"])


class TokenResponse(CustomModel):
    expiration: datetime_pd = Field(examples=[1686088809])
    created: datetime_pd = Field(examples=[1686088809])
    secret: str = Field(examples=["CQE-CTXVFCYoUpxz_6VKrHhzHaUZv68XvxV-3AvQbnA"])


class AuthTokenInfoResponse(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    created: datetime_pd = Field(examples=[1686088809])
    client: ClientResponse | None = Field(
        description="Information about logged by third-party client"
    )
    scope: list[str]
    expiration: datetime_pd = Field(examples=[1686088809])
    used: datetime_pd | None = Field(examples=[1686088809, None])


class AuthTokenInfoPaginationResponse(CustomModel):
    list: list[AuthTokenInfoResponse]
    pagination: PaginationResponse


class TokenRequestResponse(CustomModel):
    reference: str
    redirect_url: str
    expiration: datetime_pd = Field(examples=[1686088809])


class TokenRequestArgs(CustomModel):
    scope: list[str] = Field(
        examples=[constants.ALL_SCOPES + list(constants.SCOPE_GROUPS)]
    )


class TokenProceedArgs(CustomModel):
    request_reference: uuid.UUID
    client_secret: str
