from app.common.utils import calculate_document_length
from pydantic import Field, field_validator
from app.common.schemas import Document
from pydantic import ValidationError
from app.schemas import CustomModel


class DocumentArgs(CustomModel):
    document: list[dict] = Field(min_length=1)

    @field_validator("document")
    def validate_document_length(cls, document: list[dict]):
        try:
            Document(nodes=document)
        except ValidationError as e:
            raise ValueError(f"Invalid document structure: {e}") from e

        max_length = 65536

        if calculate_document_length(document) > max_length:
            raise ValueError(
                f"Total document length exceeds {max_length} characters"
            )

        return document
