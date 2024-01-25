from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Edit, EditComment
from .schemas import ContentTypeEnum
from sqlalchemy import select
from app import constants
from .utils import is_int

# This part inspited by edit logic
# If we change edit logic we probably change this as well
content_type_to_content_class = {
    constants.CONTENT_SYSTEM_EDIT: Edit,
}

content_type_to_comment_class = {
    constants.CONTENT_SYSTEM_EDIT: EditComment,
}


async def get_content_by_slug(
    session: AsyncSession, content_type: ContentTypeEnum, slug: str
):
    content_model = content_type_to_content_class[content_type]
    query = select(content_model)

    # Special case for edit
    if content_type == constants.CONTENT_SYSTEM_EDIT:
        if not is_int(slug):
            return None

        query = query.filter(content_model.edit_id == int(slug))

    # Everything else is handled here
    else:
        query = query.filter(content_model.slug == slug)

    return await session.scalar(query)
