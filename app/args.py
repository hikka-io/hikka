# Shared args between different endpoints

from pydantic import BaseModel, Field

class PaginationArgs(BaseModel):
    page: int = Field(default=1, gt=0)
