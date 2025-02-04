from app.common.schemas import DocumentText, DocumentElement


def calculate_document_length(elements: list[DocumentElement]) -> int:
    total_length = 0

    for element in elements:
        if isinstance(element, DocumentText):
            total_length += len(element.text or "")

        elif hasattr(element, "children"):
            total_length += calculate_document_length(element.children)

    return total_length


def find_document_images(elements: list[dict]) -> list[dict]:
    images = []

    for element in elements:
        if element.get("type") == "image":
            images.append(element)

        if "children" in element and isinstance(element["children"], list):
            images.extend(find_document_images(element["children"]))

    return images
