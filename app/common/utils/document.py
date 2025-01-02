from app.common.schemas import DocumentText, DocumentElement


def calculate_text_length(elements: list[DocumentElement]) -> int:
    total_length = 0

    for element in elements:
        if isinstance(element, DocumentText):
            total_length += len(element.text or "")

        elif hasattr(element, "children"):
            total_length += calculate_text_length(element.children)

    return total_length
