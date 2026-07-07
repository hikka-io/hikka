from pydantic import field_validator
from app.schemas import CustomModel
from pydantic import Field, AnyUrl
from urllib.parse import urlparse
from typing import Literal
from enum import Enum


# Enums
class DocumentLinkTargetEnum(str, Enum):
    _parent = "_parent"
    _blank = "_blank"
    _self = "_self"
    _top = "_top"


# Args
class DocumentNode(CustomModel):
    id: str | None = None


class DocumentText(DocumentNode):
    italic: bool | None = None
    bold: bool | None = None
    text: str


class DocumentLink(DocumentNode):
    target: DocumentLinkTargetEnum = Field(default=None)
    children: list["DocumentElement"]
    type: Literal["a"]
    url: str


class DocumentParagraph(DocumentNode):
    children: list["DocumentElement"]
    type: Literal["p"]


class DocumentBlockquote(DocumentNode):
    children: list["DocumentElement"]
    type: Literal["blockquote"]


class DocumentSpoiler(DocumentNode):
    children: list["DocumentElement"]
    type: Literal["spoiler"]


class DocumentLic(DocumentNode):
    children: list["DocumentElement"]
    type: Literal["lic"]


class DocumentLi(DocumentNode):
    children: list[DocumentLic]
    type: Literal["li"]


class DocumentUl(DocumentNode):
    children: list[DocumentLi]
    type: Literal["ul"]


class DocumentOl(DocumentNode):
    children: list[DocumentLi]
    type: Literal["ol"]


class DocumentH3(DocumentNode):
    children: list[DocumentText] = Field(max_length=1)
    type: Literal["h3"]


class DocumentH4(DocumentNode):
    children: list[DocumentText] = Field(max_length=1)
    type: Literal["h4"]


class DocumentH5(DocumentNode):
    children: list[DocumentText] = Field(max_length=1)
    type: Literal["h5"]


class DocumentImage(DocumentNode):
    children: list[DocumentText] = Field(max_length=1)
    type: Literal["image"]
    url: AnyUrl


class DocumentVideo(DocumentNode):
    children: list[DocumentText] = Field(max_length=1)
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


class DocumentImageGroup(DocumentNode):
    children: list[DocumentImage] = Field(max_length=4)
    type: Literal["image_group"]


class DocumentTableCell(DocumentNode):
    children: list["DocumentElement"]
    type: Literal["td", "th"]
    colSpan: int | None = Field(default=None, ge=1)
    rowSpan: int | None = Field(default=None, ge=1)


class DocumentTableRow(DocumentNode):
    children: list[DocumentTableCell]
    type: Literal["tr"]


class DocumentTable(DocumentNode):
    children: list[DocumentTableRow]
    type: Literal["table"]


DocumentElement = (
    DocumentParagraph
    | DocumentBlockquote
    | DocumentSpoiler
    | DocumentLink
    | DocumentText
    | DocumentH3
    | DocumentH4
    | DocumentH5
    | DocumentUl
    | DocumentOl
    | DocumentVideo
    | DocumentImageGroup
    | DocumentTable
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

        def validate_children(children, current_depth=1, is_root=False):
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

            for index, element in enumerate(children):
                if not isinstance(element, dict):
                    raise ValueError("Invalid children element")

                if "children" in element:
                    validate_children(element["children"], current_depth + 1)

        validate_children(document, is_root=True)

        return document
