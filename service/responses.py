# Shared responses between different endpoints

from pydantic import BaseModel

class PaginationResponse(BaseModel):
    total: int
    pages: int
    page: int
