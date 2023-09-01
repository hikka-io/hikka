from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Anime, ContentEdit
from datetime import datetime
from app import constants

from .schemas import (
    EditAnimeArgs,
)


async def create_anime_edit_request(
    args: EditAnimeArgs,
    user: User,
    anime: Anime,
    session: AsyncSession,
) -> ContentEdit:
    # Pretty much the only reason we convert it to dict here is so that we can
    # get rid of non-edit fields like "description" in a neat way
    args = args.dict()
    description = args.pop("description")

    previous = {}
    changes = {}

    for key, value in args.items():
        if not value:
            continue

        previous[key] = getattr(anime, key)
        changes[key] = value

    now = datetime.utcnow()

    edit = ContentEdit(
        **{
            "status": constants.EDIT_PENDING,
            "content_id": anime.id,
            "content_type": constants.CONTENT_ANIME,
            "previous": previous,
            "changes": changes,
            "created": now,
            "updated": now,
            "author": user,
            "description": description,
        }
    )

    session.add(edit)
    await session.commit()

    return edit
