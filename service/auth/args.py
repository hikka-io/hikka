from pydantic import BaseModel, EmailStr, Field

class SignupArgs(BaseModel):
    username: str = Field(max_length=64, regex="[A-Za-z0-9]")
    password: str = Field(min_length=8, max_length=64)
    email: EmailStr

class LoginArgs(BaseModel):
    password: str = Field(min_length=8, max_length=64)
    email: EmailStr
