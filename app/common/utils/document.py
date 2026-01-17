from app.common.schemas import DocumentText, DocumentElement
import string
import copy


def generate_preview(raw_document, max_length=300):
    # If we don't do a deep copy here raw article document will
    # be botched somewhere down the line
    article_document = copy.deepcopy(raw_document)

    total_characters = 0
    media_found = False
    END = "..."

    def _truncate(text: str, limit: int) -> str:
        if limit <= 0:
            return END

        truncated = text[:limit]
        space_pos = truncated.rfind(" ")

        if space_pos != -1:
            truncated = truncated[:space_pos]

        truncated = truncated.rstrip(string.punctuation + " ")

        return truncated + END

    def _process_document(document):
        nonlocal total_characters
        nonlocal media_found

        result = []

        for node in document:
            if total_characters >= max_length:
                break

            if "children" in node:
                node["children"] = _process_document(node["children"])

                if node["type"] == "preview":
                    result.extend(node["children"])
                    continue

            if "text" in node:
                text_len = len(node["text"])
                if total_characters + text_len > max_length:
                    remaining = max_length - total_characters

                    truncated_text = _truncate(
                        node["text"], remaining - len(END)
                    )

                    node["text"] = truncated_text
                    total_characters = max_length
                    result.append(node)
                    break

                else:
                    total_characters += text_len

            if node.get("type") in ["image_group", "video"]:
                if media_found:
                    continue

                media_found = True

            result.append(node)

        return result

    return _process_document(article_document)


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
