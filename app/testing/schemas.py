from app.common.utils import calculate_document_length
from app.common.schemas import DocumentElement
from pydantic import Field, field_validator
from app.schemas import CustomModel


class DocumentArgs(CustomModel):
    document: list[DocumentElement] = Field(min_length=1)

    @field_validator("document", mode="before")
    def validate_raw(cls, document: list[dict]) -> list[dict]:
        if not isinstance(document, list):
            return document

        children = [document]
        while children:
            child = children.pop(0)
            for element in child.copy():
                assert isinstance(element, dict), "Invalid children element"

                if "children" in element:
                    children.append(element["children"])

        return document

    @field_validator("document")
    def validate_text_length(cls, document: list[DocumentElement]):
        max_length = 5000

        if calculate_document_length(document) > max_length:
            raise ValueError(
                f"Total text length exceeds {max_length} characters."
            )

        return document
