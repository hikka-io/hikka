from app.common.schemas import Document

# from pydantic import ValidationError


async def test_document():
    Document(
        nodes=[
            {"text": "Test text"},
            {"text": "Test italic text", "italic": True},
            {"text": "Test bold text", "bold": True},
        ]
    )
