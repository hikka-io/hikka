from app.common.utils import find_document_images


async def test_document_utils():
    images = find_document_images(
        [
            {"text": "Text node"},
            {
                "type": "image_group",
                "children": [
                    {"type": "image", "url": "https://cdn.hikka.io/image1.jpg"},
                    {"type": "image", "url": "https://cdn.hikka.io/image2.jpg"},
                    {"type": "image", "url": "https://cdn.hikka.io/image3.jpg"},
                ],
            },
        ]
    )

    assert len(images) == 3
