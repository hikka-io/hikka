# Shared schemas between different routes

from pydantic import BaseModel, Field


class PaginationArgs(BaseModel):
    page: int = Field(default=1, gt=0)


class PaginationResponse(BaseModel):
    total: int
    pages: int
    page: int
