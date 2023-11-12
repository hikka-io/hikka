from pydantic import ValidationError
from app import constants

from .schemas import (
    ContentTypeEnum,
    PersonEditArgs,
    AnimeEditArgs,
    EditArgs,
)


def check_edit_schema(
    content_type: ContentTypeEnum,
    args: EditArgs,
):
    # Make sure we know how to validate proposed content changes
    schemas = {
        constants.CONTENT_PERSON: PersonEditArgs,
        constants.CONTENT_ANIME: AnimeEditArgs,
    }

    if not (schema := schemas.get(content_type)):
        return False

    # Validate after field with provided schema
    # This checks heavily depends on Pydantic's Extra.forbid option enabled
    try:
        schema(**args.after)
    except ValidationError:
        return False

    return True
