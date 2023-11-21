from datetime import datetime
from pydantic import Field

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
    expiration: datetime = Field(examples=[1686088809])
    created: datetime = Field(examples=[1686088809])
    secret: str = Field(
        examples=["CQE-CTXVFCYoUpxz_6VKrHhzHaUZv68XvxV-3AvQbnA"]
    )
