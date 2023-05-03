from pydantic import BaseModel, Field
from typing import Union

class DescriptionArgs(BaseModel):
    description: Union[str, None] = Field(default=None, max_length=140)
