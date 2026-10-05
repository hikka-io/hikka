from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from app.service import get_my_score_subquery
from sqlalchemy import select, exists
from app import constants
from uuid import UUID

from sqlalchemy.orm import (
    with_expression,
    joinedload,
)

from app.models import (
    CharacterCollectionContent,
    PersonCollectionContent,
    AnimeCollectionContent,
    MangaCollectionContent,
    NovelCollectionContent,
    CollectionMember,
    CollectionContent,
    Collection,
    AnimeWatch,
    MangaRead,
    NovelRead,
    Anime,
    Manga,
    Novel,
    User,
)


def get_my_collection_role_subquery(request_user: User | None):

    return (
        select(CollectionMember.role)
        .filter(
            CollectionMember.user_id == request_user.id
            if request_user
            else False,
            CollectionMember.collection_id == Collection.id,
            CollectionMember.status == constants.COLLECTION_MEMBER_ACCEPTED,
        )
        .scalar_subquery()
    )


def collections_load_options(
    query: Select, request_user: User | None, preview: bool = False
):
    anime_watch_criteria = with_loader_criteria(
        AnimeWatch,
        AnimeWatch.user_id == request_user.id if request_user else False,
    )

    manga_read_criteria = with_loader_criteria(
        MangaRead,
        MangaRead.user_id == request_user.id if request_user else False,
    )

    novel_read_criteria = with_loader_criteria(
        NovelRead,
        NovelRead.user_id == request_user.id if request_user else False,
    )

    anime_options = (
        joinedload(Collection.collection.of_type(AnimeCollectionContent))
        .joinedload(AnimeCollectionContent.content)
        .joinedload(Anime.watch),
        anime_watch_criteria,
    )

    manga_options = (
        joinedload(Collection.collection.of_type(MangaCollectionContent))
        .joinedload(MangaCollectionContent.content)
        .joinedload(Manga.read),
        manga_read_criteria,
    )

    novel_options = (
        joinedload(Collection.collection.of_type(NovelCollectionContent))
        .joinedload(NovelCollectionContent.content)
        .joinedload(Novel.read),
        novel_read_criteria,
    )

    character_options = (
        joinedload(
            Collection.collection.of_type(CharacterCollectionContent)
        ).joinedload(CharacterCollectionContent.content),
    )

    person_options = (
        joinedload(
            Collection.collection.of_type(PersonCollectionContent)
        ).joinedload(PersonCollectionContent.content),
    )

    options = [
        *anime_options,
        *manga_options,
        *novel_options,
        *character_options,
        *person_options,
    ]

    options.append(
        with_expression(
            Collection.my_score,
            get_my_score_subquery(
                Collection, constants.CONTENT_COLLECTION, request_user
            ),
        )
    )

    options.append(
        with_expression(
            Collection.my_role,
            get_my_collection_role_subquery(request_user),
        )
    )

    if preview:
        options.append(
            with_loader_criteria(
                CollectionContent, CollectionContent.order <= 6
            )
        )

    return query.options(*options)


async def get_collection_member(
    session: AsyncSession,
    collection_id: UUID,
    user: User | None,
    status: str | None = constants.COLLECTION_MEMBER_ACCEPTED,
) -> CollectionMember | None:
    """
    Single source of truth for collection permissions

    Collection.author_id is only a record of who created the collection,
    it grants nothing. Permission checks read membership through here, or
    through is_collection_owner which builds on it.
    """

    if not user:
        return None

    query = (
        select(CollectionMember)
        .options(joinedload(CollectionMember.user))
        .filter(
            CollectionMember.collection_id == collection_id,
            CollectionMember.user_id == user.id,
        )
    )

    if status:
        query = query.filter(CollectionMember.status == status)

    return await session.scalar(query)


async def is_collection_owner(
    session: AsyncSession, collection_id: UUID, user: User | None
) -> bool:
    member = await get_collection_member(session, collection_id, user)
    return bool(member) and member.role == constants.COLLECTION_MEMBER_OWNER


def collection_member_exists(user_id: UUID):
    """EXISTS clause correlated on Collection, for list filters"""

    return exists(
        select(CollectionMember.id)
        .where(
            CollectionMember.collection_id == Collection.id,
            CollectionMember.user_id == user_id,
            CollectionMember.status == constants.COLLECTION_MEMBER_ACCEPTED,
        )
        .correlate(Collection)
    )
