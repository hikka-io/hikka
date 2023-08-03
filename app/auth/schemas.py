from pydantic import EmailStr, Field
from app.schemas import ORJSONModel
from datetime import datetime
from typing import Union


# Args
class TokenArgs(ORJSONModel):
    token: str = Field(example="CQE-CTXVFCYoUpxz_6VKrHhzHaUZv68XvxV-3AvQbnA")


class EmailArgs(ORJSONModel):
    email: EmailStr = Field(example="hikka@email.com")


class UsernameArgs(ORJSONModel):
    username: str = Field(max_length=16, regex="[A-Za-z0-9]", example="hikka")


class SignupArgs(ORJSONModel):
    username: str = Field(max_length=16, regex="[A-Za-z0-9]", example="hikka")
    password: str = Field(min_length=8, max_length=64, example="password")
    email: EmailStr = Field(example="hikka@email.com")


class LoginArgs(ORJSONModel):
    password: str = Field(min_length=8, max_length=64, example="password")
    email: EmailStr = Field(example="hikka@email.com")


class ComfirmResetArgs(ORJSONModel):
    password: str = Field(min_length=8, max_length=64, example="password")
    token: str = Field(example="CQE-CTXVFCYoUpxz_6VKrHhzHaUZv68XvxV-3AvQbnA")


class CodeArgs(ORJSONModel):
    code: str


# Responses
class UserResponse(ORJSONModel):
    created: datetime = Field(example=1686088809)
    username: Union[str, None] = Field(example="hikka")


class ProviderUrlResponse(ORJSONModel):
    url: str = Field(example="https://accounts.google.com/o/oauth2/v2/auth")


class TokenResponse(ORJSONModel):
    secret: str = Field(example="CQE-CTXVFCYoUpxz_6VKrHhzHaUZv68XvxV-3AvQbnA")
    expiration: datetime = Field(example=1686088809)
    created: datetime = Field(example=1686088809)
