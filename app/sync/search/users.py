from meilisearch_python_sdk.models.settings import MeilisearchSettings
from app.utils import get_settings, to_timestamp
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from sqlalchemy import select
from app.models import User
from app import constants
from uuid import UUID
from . import service


async def update_user_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            searchable_attributes=["username"],
            filterable_attributes=["created"],
            displayed_attributes=["username"],
            sortable_attributes=["created"],
            distinct_attribute="username",
        )
    )


def user_to_document(user: User):
    return {
        "created": to_timestamp(user.created),
        "username": user.username,
        "id": user.reference,
    }


async def user_documents(
    session: AsyncSession, limit: int, last_id: UUID | None
):
    query = (
        select(User).filter(User.needs_search_update == True)  # noqa: E712
    )

    return await service.get_documents(
        session, query, User.id, user_to_document, limit, last_id
    )


async def update_search_users():
    settings = get_settings()

    async with sessionmanager.session() as session:
        async with AsyncClient(**settings.meilisearch) as client:
            index = client.index(constants.SEARCH_INDEX_USERS)

            await update_user_settings(index)

            await service.index_documents(session, index, user_documents)
