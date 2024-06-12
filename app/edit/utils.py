from pydantic import ValidationError
from app.models import Edit
from app import constants

from .schemas import (
    CharacterEditArgs,
    EditContentTypeEnum,
    PersonEditArgs,
    AnimeEditArgs,
    MangaEditArgs,
    NovelEditArgs,
    EditArgs,
)


def check_edit_schema(
    content_type: EditContentTypeEnum,
    args: EditArgs,
):
    # Make sure we know how to validate proposed content changes
    schemas = {
        constants.CONTENT_CHARACTER: CharacterEditArgs,
        constants.CONTENT_PERSON: PersonEditArgs,
        constants.CONTENT_ANIME: AnimeEditArgs,
        constants.CONTENT_MANGA: MangaEditArgs,
        constants.CONTENT_NOVEL: NovelEditArgs,
    }

    if not (schema := schemas.get(content_type)):
        return False

    # Validate after field with provided schema
    # This check heavily depends on Pydantic's extra="forbid" option
    try:
        schema(**args.after)
    except ValidationError:
        return False

    return True


def check_invalid_fields(edit: Edit):
    """Check if content has unknown fields"""

    for key, _ in edit.after.items():
        if not hasattr(edit.content, key):
            return True

    return False


def check_after(after, content):
    """Check if Edit has differences from content"""

    pop_list = []

    for key, value in after.items():
        if getattr(content, key) == value:
            pop_list.append(key)

    for pop_key in pop_list:
        after.pop(pop_key)

    return after


def calculate_before(content, after):
    before = {}

    for key, _ in after.items():
        before[key] = getattr(content, key)

    return before
