from app.common.utils import calculate_text_length
from app.common.schemas import DocumentElement
from pydantic import Field, field_validator
from app.schemas import CustomModel


class DocumentArgs(CustomModel):
    document: list[DocumentElement] = Field(min_length=1)

    @field_validator("document")
    def validate_text_length(cls, document: list[DocumentElement]):
        max_length = 5000

        if calculate_text_length(document) > max_length:
            raise ValueError(
                f"Total text length exceeds {max_length} characters."
            )

        return document
