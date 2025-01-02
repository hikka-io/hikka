from app.common.schemas import DocumentText, DocumentElement


def calculate_document_length(elements: list[DocumentElement]) -> int:
    total_length = 0

    for element in elements:
        if isinstance(element, DocumentText):
            total_length += len(element.text or "")

        elif hasattr(element, "children"):
            total_length += calculate_document_length(element.children)

    return total_length
