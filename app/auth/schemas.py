from app import constants
from app.schemas import datetime_pd, ClientResponse
from pydantic import Field
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


class LoginArgs(PasswordArgs, EmailArgs):
    pass


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
    secret: str = Field(
        examples=["CQE-CTXVFCYoUpxz_6VKrHhzHaUZv68XvxV-3AvQbnA"]
    )


class AuthInfoResponse(CustomModel):
    created: datetime_pd = Field(examples=[1686088809])
    client: ClientResponse | None = Field(
        description="Information about logged by third-party client"
    )
    scope: list[str]
    expiration: datetime_pd = Field(examples=[1686088809])


class TokenRequestResponse(CustomModel):
    reference: str
    redirect_url: str
    expiration: datetime_pd = Field(examples=[1686088809])


class TokenRequestArgs(CustomModel):
    scope: list[str] = Field(
        examples=[constants.ALL_SCOPES + list(constants.SCOPE_ALIASES)]
    )


class TokenProceedArgs(CustomModel):
    request_reference: uuid.UUID
    client_secret: str
