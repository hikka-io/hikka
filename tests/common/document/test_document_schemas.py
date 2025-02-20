from app.common.schemas import Document
from pydantic import ValidationError


async def test_document():
    Document(
        nodes=[
            {
                "type": "preview",
                "children": [
                    {"text": "Test text"},
                ],
            },
            {"text": "Test text"},
            {"text": "Test italic text", "italic": True},
            {"text": "Test bold text", "bold": True},
            {"text": ""},
        ]
    )


async def test_document_bad_preview():
    no_preview_failed = False
    not_first_preview_failed = False
    two_preview_failed = False
    nested_preview_failed = False
    extra_nested_preview_failed = False

    try:
        Document(nodes=[{"text": "Test text"}])
    except ValidationError:
        no_preview_failed = True

    try:
        Document(
            nodes=[
                {"text": "Test text"},
                {"type": "preview", "children": [{"text": "Test text"}]},
            ]
        )
    except ValidationError:
        not_first_preview_failed = True

    try:
        Document(
            nodes=[
                {"type": "preview", "children": [{"text": "Test text"}]},
                {"type": "preview", "children": [{"text": "Test text"}]},
            ]
        )
    except ValidationError:
        two_preview_failed = True

    try:
        Document(
            nodes=[
                {
                    "type": "p",
                    "children": [
                        {
                            "type": "preview",
                            "children": [{"text": "Test text"}],
                        }
                    ],
                },
            ]
        )
    except ValidationError:
        nested_preview_failed = True

    try:
        Document(
            nodes=[
                {"type": "preview", "children": [{"text": "Test text"}]},
                {
                    "type": "p",
                    "children": [
                        {
                            "type": "preview",
                            "children": [{"text": "Test text"}],
                        }
                    ],
                },
            ]
        )
    except ValidationError:
        extra_nested_preview_failed = True

    assert no_preview_failed is True
    assert not_first_preview_failed is True
    assert two_preview_failed is True
    assert nested_preview_failed is True
    assert extra_nested_preview_failed is True
