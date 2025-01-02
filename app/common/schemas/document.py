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


DocumentElement = (
    DocumentParagraph
    | DocumentBlockquote
    | DocumentSpoiler
    | DocumentLink
    | DocumentText
)


class DocumentArgs(CustomModel):
    document: list[DocumentElement]
