from app.common.schemas import Document
from pydantic import ValidationError


async def test_document():
    Document(
        nodes=[
            {
                "type": "preview",
                "children": [
                    {"children": [{"text": ""}], "type": "p"},
                    {
                        "type": "image_group",
                        "children": [
                            {
                                "type": "image",
                                "children": [{"text": ""}],
                                "url": "https://cdn.hikka.io/uploads/olexh/attachment/e0087ef1-4c61-40d9-b43b-449c0a594ed9.jpg",
                            },
                            {
                                "type": "image",
                                "url": "https://cdn.hikka.io/uploads/olexh/attachment/b1bd6734-1aa5-49fe-a637-61acc2000436.jpg",
                                "children": [{"text": ""}],
                            },
                        ],
                    },
                    {"children": [{"text": ""}], "type": "p"},
                ],
            },
            {
                "type": "p",
                "children": [
                    {
                        "type": "h3",
                        "children": [{"text": "H3 Title"}],
                    },
                    {
                        "type": "h4",
                        "children": [{"text": "H4 Title"}],
                    },
                    {
                        "type": "h5",
                        "children": [{"text": "H5 Title"}],
                    },
                ],
            },
            {"type": "p", "children": [{"text": ""}]},
            {"type": "blockquote", "children": [{"text": "testsstt"}]},
            {
                "type": "spoiler",
                "children": [
                    {"type": "p", "children": [{"text": "tesrfadsadsa"}]}
                ],
            },
            {
                "type": "p",
                "children": [
                    {"text": ""},
                    {
                        "target": "_parent",
                        "url": "https://google.com",
                        "type": "a",
                        "children": [{"text": "Link"}],
                    },
                    {
                        "url": "https://google.com",
                        "type": "a",
                        "children": [{"text": "Link"}],
                    },
                    {"text": ""},
                ],
            },
            {"type": "p", "children": [{"text": ""}]},
            {
                "type": "ul",
                "children": [
                    {
                        "type": "li",
                        "children": [
                            {"type": "lic", "children": [{"text": "fdfdsfs"}]}
                        ],
                    },
                    {
                        "type": "li",
                        "children": [
                            {"type": "lic", "children": [{"text": "fsdfsdf"}]}
                        ],
                    },
                    {
                        "type": "li",
                        "children": [
                            {"type": "lic", "children": [{"text": "fsdf"}]}
                        ],
                    },
                ],
            },
            {"type": "p", "children": [{"text": ""}]},
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
