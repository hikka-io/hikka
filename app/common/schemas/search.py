from app.schemas import ContentStatusEnum
from pydantic import Field


class ReadSearchBaseMixin:
    status: list[ContentStatusEnum] = []
    only_translated: bool = False
    magazines: list[str] = []
    genres: list[str] = []

    score: list[int | None] = Field(
        default=[None, None],
        min_length=2,
        max_length=2,
        examples=[[0, 10]],
    )

    native_score: list[int | None] = Field(
        default=[None, None],
        min_length=2,
        max_length=2,
        examples=[[0, 10]],
    )
