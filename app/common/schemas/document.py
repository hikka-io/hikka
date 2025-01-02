from app.schemas import CustomModel
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


DocumentElement = (
    DocumentParagraph
    | DocumentBlockquote
    | DocumentSpoiler
    | DocumentLink
    | DocumentText
    | DocumentUl
    | DocumentOl
)
