from pydantic import field_validator
from app.schemas import CustomModel
from pydantic import Field, AnyUrl
from urllib.parse import urlparse
from typing import Literal


# Args
class DocumentText(CustomModel):
    italic: bool | None = None
    bold: bool | None = None
    text: str


class DocumentLink(CustomModel):
    children: list["DocumentElement"]
    type: Literal["a"]
    url: str


class DocumentParagraph(CustomModel):
    children: list["DocumentElement"]
    type: Literal["p"]


class DocumentBlockquote(CustomModel):
    children: list["DocumentElement"]
    type: Literal["blockquote"]


class DocumentSpoiler(CustomModel):
    children: list["DocumentElement"]
    type: Literal["spoiler"]


class DocumentLic(CustomModel):
    children: list["DocumentElement"]
    type: Literal["lic"]


class DocumentLi(CustomModel):
    children: list[DocumentLic]
    type: Literal["li"]


class DocumentUl(CustomModel):
    children: list[DocumentLi]
    type: Literal["ul"]


class DocumentOl(CustomModel):
    children: list[DocumentLi]
    type: Literal["ol"]


class DocumentImage(CustomModel):
    type: Literal["image"]
    url: AnyUrl


class DocumentVideo(CustomModel):
    type: Literal["video"]
    url: AnyUrl

    @field_validator("url")
    @classmethod
    def check_url(cls, url: AnyUrl) -> AnyUrl:
        hostname = urlparse(str(url)).hostname

        if not hostname or not any(
            endpoint in hostname for endpoint in ["youtube.com"]
        ):
            raise ValueError("Invalid video url")

        return url


class DocumentMedia(CustomModel):
    children: list[DocumentImage] = Field(max_length=4)
    type: Literal["media"]


DocumentElement = (
    DocumentParagraph
    | DocumentBlockquote
    | DocumentSpoiler
    | DocumentLink
    | DocumentText
    | DocumentUl
    | DocumentOl
    | DocumentMedia
)


class Document(CustomModel):
    nodes: list[DocumentElement]

    # Credit: https://github.com/hikka-io/hikka/pull/358
    @field_validator("nodes", mode="before")
    def validate_raw(cls, document: list[dict]) -> list[dict]:
        total_elements = 0

        max_elements = 1000
        max_depth = 10

        if not isinstance(document, list):
            return document

        def validate_children(children, current_depth=1):
            nonlocal total_elements
            total_elements += len(children)

            if total_elements > max_elements:
                raise ValueError(
                    f"Document structure exceeds maximum number of {max_elements} elements"
                )

            if current_depth > max_depth:
                raise ValueError(
                    f"Document structure exceeds maximum depth of {max_depth}"
                )

            for element in children:
                if not isinstance(element, dict):
                    raise ValueError("Invalid children element")

                if "children" in element:
                    validate_children(element["children"], current_depth + 1)

        validate_children(document)
        return document
