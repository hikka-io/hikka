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
class DocumentText(CustomModel):
    italic: bool | None = None
    bold: bool | None = None
    text: str


class DocumentLink(CustomModel):
    target: DocumentLinkTargetEnum = Field(default=None)
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


class DocumentH3(CustomModel):
    children: list[DocumentText] = Field(max_length=1)
    type: Literal["h3"]


class DocumentH4(CustomModel):
    children: list[DocumentText] = Field(max_length=1)
    type: Literal["h4"]


class DocumentH5(CustomModel):
    children: list[DocumentText] = Field(max_length=1)
    type: Literal["h5"]


class DocumentImage(CustomModel):
    children: list[DocumentText] = Field(max_length=1)
    type: Literal["image"]
    url: AnyUrl


class DocumentPreview(CustomModel):
    children: list["DocumentElement"]
    type: Literal["preview"]


class DocumentVideo(CustomModel):
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


class DocumentImageGroup(CustomModel):
    children: list[DocumentImage] = Field(max_length=4)
    type: Literal["image_group"]


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
    | DocumentPreview
    | DocumentVideo
    | DocumentImageGroup
)


class Document(CustomModel):
    nodes: list[DocumentElement]

    # Credit: https://github.com/hikka-io/hikka/pull/358
    @field_validator("nodes", mode="before")
    def validate_raw(cls, document: list[dict]) -> list[dict]:
        total_elements = 0
        preview_found = False
        max_elements = 1000
        max_depth = 10

        if not isinstance(document, list):
            return document

        def validate_children(children, current_depth=1, is_root=False):
            nonlocal total_elements, preview_found

            if is_root:
                # Ensure the first element is a preview if it exists at all
                if children and children[0].get("type") == "preview":
                    preview_found = True
                else:
                    if any(
                        child.get("type") == "preview" for child in children
                    ):
                        raise ValueError(
                            "DocumentPreview must be the first element in the document"
                        )

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

                if element.get("type") == "preview":
                    if not is_root:
                        raise ValueError(
                            "DocumentPreview must be at the top level"
                        )

                    if index != 0:
                        raise ValueError(
                            "DocumentPreview must be the first element"
                        )

                if "children" in element:
                    validate_children(element["children"], current_depth + 1)

        validate_children(document, is_root=True)

        # TODO: if we decide to make preview required
        # we just need to enable this check
        # if not preview_found:
        #     raise ValueError("DocumentPreview must be present")

        return document
