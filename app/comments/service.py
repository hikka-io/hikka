from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, func
from .utils import uuid_to_path, round_hour
from sqlalchemy.orm import with_expression
from sqlalchemy.orm import immediateload
from sqlalchemy.orm import joinedload
from .schemas import ContentTypeEnum
from sqlalchemy_utils import Ltree
from uuid import UUID, uuid4
from app.utils import utcnow
from app import constants
from app import utils
import copy

from app.service import (
    get_my_score_subquery,
    create_log,
)


from app.models import (
    CollectionContent,
    CollectionComment,
    CharacterEdit,
    AnimeComment,
    EditComment,
    Collection,
    PersonEdit,
    AnimeEdit,
    Character,
    Comment,
    Person,
    Anime,
    User,
    Edit,
)


content_type_to_comment_class = {
    constants.CONTENT_COLLECTION: CollectionComment,
    constants.CONTENT_SYSTEM_EDIT: EditComment,
    constants.CONTENT_ANIME: AnimeComment,
}


async def get_comment(
    session: AsyncSession,
    comment_reference: UUID,
    request_user: User | None,
) -> Comment:
    return await session.scalar(
        select(Comment)
        .filter(
            Comment.id == comment_reference,
            Comment.deleted == False,  # noqa: E712
        )
        .options(
            with_expression(
                Comment.my_score,
                get_my_score_subquery(
                    Comment, constants.CONTENT_COMMENT, request_user
                ),
            )
        )
    )


async def create_comment(
    session: AsyncSession,
    content_type: ContentTypeEnum,
    content_id: str,
    author: User,
    text: str,
    parent: Comment | None = None,
):
    cleaned_text = utils.remove_bad_characters(text)
    comment_model = content_type_to_comment_class[content_type]
    now = utcnow()

    comment = comment_model(
        **{
            "content_type": content_type,
            "content_id": content_id,
            "text": cleaned_text,
            "private": False,
            "author": author,
            "vote_score": 0,
            "created": now,
            "updated": now,
            "id": uuid4(),
            "score": 0,
        }
    )

    # Here we handle comments for private collections
    if content_type == constants.CONTENT_COLLECTION:
        visibility = await session.scalar(
            select(Collection.visibility).filter(Collection.id == content_id)
        )

        if visibility == constants.COLLECTION_PRIVATE:
            comment.private = True

    ltree_id = Ltree(uuid_to_path(comment.id))
    comment.path = ltree_id if parent is None else parent.path + ltree_id

    session.add(comment)
    await session.commit()

    await create_log(
        session,
        constants.LOG_COMMENT_WRITE,
        author,
        comment.id,
        {"content_type": comment.content_type},
    )

    return comment


async def get_comment_by_content(
    session: AsyncSession,
    content_type: ContentTypeEnum,
    content_id: str,
    reference: str,
) -> Comment | None:
    return await session.scalar(
        select(Comment).filter(
            Comment.deleted == False,  # noqa: E712
            Comment.content_type == content_type,
            Comment.content_id == content_id,
            Comment.id == reference,
        )
    )


async def count_comments_by_content_id(
    session: AsyncSession, content_id: str
) -> int:
    """Count comments for given content"""

    return await session.scalar(
        select(func.count(Comment.id)).filter(
            func.nlevel(Comment.path) == 1,
            Comment.content_id == content_id,
            Comment.deleted == False,  # noqa: E712
            Comment.hidden == False,  # noqa: E712
        )
    )


async def get_comments_by_content_id(
    session: AsyncSession,
    content_id: str,
    request_user: User | None,
    limit: int,
    offset: int,
) -> list[Edit]:
    """Return comemnts for given content"""

    return await session.scalars(
        select(Comment)
        .filter(
            func.nlevel(Comment.path) == 1,
            Comment.content_id == content_id,
            Comment.deleted == False,  # noqa: E712
            Comment.hidden == False,  # noqa: E712
        )
        .options(
            with_expression(
                Comment.my_score,
                get_my_score_subquery(
                    Comment, constants.CONTENT_COMMENT, request_user
                ),
            )
        )
        .order_by(desc(Comment.created))
        .limit(limit)
        .offset(offset)
    )


async def get_sub_comments(
    session: AsyncSession,
    base_comment: Comment,
    request_user: User | None,
):
    return await session.scalars(
        select(Comment)
        .filter(
            Comment.deleted == False,  # noqa: E712
            Comment.path.descendant_of(base_comment.path),
            Comment.id != base_comment.id,
        )
        .options(
            with_expression(
                Comment.my_score,
                get_my_score_subquery(
                    Comment, constants.CONTENT_COMMENT, request_user
                ),
            )
        )
        .order_by(asc(Comment.created))
    )


async def count_comments_limit(session: AsyncSession, author: User) -> int:
    return await session.scalar(
        select(func.count(Comment.id)).filter(
            Comment.author == author,
            Comment.created > round_hour(utcnow()),
            Comment.deleted == False,  # noqa: E712
        )
    )


async def edit_comment(
    session: AsyncSession,
    comment: Comment,
    text: str,
) -> Comment:
    now = utcnow()

    old_text = comment.text
    comment.updated = now
    comment.text = text
    new_text = comment.text

    # SQLAlchemy quirks
    comment.history = copy.deepcopy(comment.history)
    comment.history.append(
        {
            "updated": utils.to_timestamp(now),
            "text": old_text,
        }
    )

    session.add(comment)
    await session.commit()

    await create_log(
        session,
        constants.LOG_COMMENT_EDIT,
        comment.author,
        comment.id,
        data={
            "content_type": comment.content_type,
            "old_text": old_text,
            "new_text": new_text,
        },
    )

    return comment


async def hide_comment(session: AsyncSession, comment: Comment, user: User):
    comment.updated = utcnow()
    comment.hidden_by = user
    comment.hidden = True

    session.add(comment)
    await session.commit()

    await create_log(
        session,
        constants.LOG_COMMENT_HIDE,
        user,
        comment.id,
        {"content_type": comment.content_type},
    )

    return True


async def comments_preview_display(
    session: AsyncSession, comment_ids: list[UUID]
):
    # TODO: Add preview image to comment (?)
    # NOTE: I HATE this function so much, it should be rewritten!
    comments = await session.scalars(
        select(Comment)
        .filter(Comment.id.in_(comment_ids))
        .options(immediateload(EditComment.content))
        .options(immediateload(CollectionComment.content))
        .options(immediateload(AnimeComment.content))
        .order_by(desc(Comment.created))
    )

    result = []

    for comment in comments:
        image = None

        if isinstance(comment, AnimeComment):
            image = comment.content.poster

        if isinstance(comment, EditComment):
            # This is horrible hack, but we need this to prevent SQLAlchemy bug
            # For some reason edit content is not loaded sometimes
            await session.refresh(comment.content)

            edit = await session.scalar(
                select(Edit)
                .filter(Edit.id == comment.content_id)
                .options(
                    joinedload(PersonEdit.content).joinedload(
                        Person.image_relation
                    ),
                    joinedload(AnimeEdit.content).joinedload(
                        Anime.poster_relation
                    ),
                    joinedload(CharacterEdit.content).joinedload(
                        Character.image_relation
                    ),
                )
            )

            if not edit:
                continue

            if isinstance(comment.content.content, Anime):
                image = edit.content.poster
            else:
                image = edit.content.image

        if isinstance(comment, CollectionComment):
            collection_content = await session.scalar(
                select(CollectionContent)
                .filter(CollectionContent.collection == comment.content)
                .order_by(asc(CollectionContent.order))
                .limit(1)
            )

            if comment.content.content_type == constants.CONTENT_ANIME:
                image = collection_content.content.poster

            else:
                image = collection_content.content.image

        result.append(
            {
                "content_type": comment.content_type,
                "vote_score": comment.vote_score,
                "reference": comment.reference,
                "slug": comment.content.slug,
                "created": comment.created,
                "updated": comment.updated,
                "author": comment.author,
                "depth": comment.depth,
                "text": comment.text,
                "image": image,
            }
        )

    return result


async def latest_comments(session: AsyncSession):
    comment_ids = await session.scalars(
        select(Comment.id, Comment.content_id)
        .filter(
            func.nlevel(Comment.path) == 1,
            Comment.hidden == False,  # noqa: E712
            Comment.private == False,  # noqa: E712
            Comment.deleted == False,  # noqa: E712
        )
        .group_by(Comment.id, Comment.content_id)
        .order_by(desc(Comment.created))
        .limit(3)
    )

    return await comments_preview_display(session, comment_ids)


async def count_comments(session: AsyncSession) -> int:
    """Count comments"""

    return await session.scalar(
        select(func.count(Comment.id)).filter(
            func.nlevel(Comment.path) == 1,
            Comment.hidden == False,  # noqa: E712
            Comment.private == False,  # noqa: E712
            Comment.deleted == False,  # noqa: E712
        )
    )


async def get_comments(session: AsyncSession, limit: int, offset: int):
    comment_ids = await session.scalars(
        select(Comment.id, Comment.content_id)
        .filter(
            func.nlevel(Comment.path) == 1,
            Comment.hidden == False,  # noqa: E712
            Comment.private == False,  # noqa: E712
            Comment.deleted == False,  # noqa: E712
        )
        .order_by(desc(Comment.created))
        .limit(limit)
        .offset(offset)
    )

    return await comments_preview_display(session, comment_ids)
