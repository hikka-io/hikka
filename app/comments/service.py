from sqlalchemy import ScalarResult, select, desc, asc, func
from .schemas import ContentTypeEnum, CommentableType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_expression
from sqlalchemy.orm import immediateload
from sqlalchemy.orm import joinedload
from app.utils import round_datetime
from sqlalchemy_utils import Ltree
from .utils import uuid_to_path
from app.utils import utcnow
from uuid import UUID, uuid4
from app import constants
from app import utils
import copy

from app.service import (
    get_my_score_subquery,
    get_content_by_id,
    create_log,
)

from app.models import (
    CollectionContent,
    CollectionComment,
    ArticleComment,
    CharacterEdit,
    AnimeComment,
    MangaComment,
    NovelComment,
    EditComment,
    Collection,
    PersonEdit,
    AnimeEdit,
    MangaEdit,
    NovelEdit,
    Character,
    Comment,
    Person,
    Anime,
    Manga,
    Novel,
    User,
    Edit,
)


content_type_to_comment_class: dict[str, type[Comment]] = {
    constants.CONTENT_COLLECTION: CollectionComment,
    constants.CONTENT_SYSTEM_EDIT: EditComment,
    constants.CONTENT_ARTICLE: ArticleComment,
    constants.CONTENT_ANIME: AnimeComment,
    constants.CONTENT_MANGA: MangaComment,
    constants.CONTENT_NOVEL: NovelComment,
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


async def get_comments_count(
    session: AsyncSession,
    content_type: ContentTypeEnum,
    content: CommentableType,
    first_level_only: bool = False,
):
    query = select(
        func.count(Comment.id).filter(
            Comment.content_type == content_type,
            Comment.content_id == content.id,
        )
    )

    if first_level_only:
        query = query.filter(func.nlevel(Comment.path) == 1)

    return await session.scalar(query)


async def create_comment(
    session: AsyncSession,
    content_type: ContentTypeEnum,
    content: CommentableType,
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
            "content_id": content.id,
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
            select(Collection.visibility).filter(Collection.id == content.id)
        )

        if visibility == constants.COLLECTION_PRIVATE:
            comment.private = True

    ltree_id = Ltree(uuid_to_path(comment.id))
    comment.path = ltree_id if parent is None else parent.path + ltree_id

    session.add(comment)
    await session.commit()

    # Update comments count here
    content.comments_count = await get_comments_count(
        session, content_type, content
    )

    content.comments_count_pagination = await get_comments_count(
        session, content_type, content, True
    )

    session.add(content)
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


async def get_comments_by_content_id(
    session: AsyncSession,
    content_id: str,
    request_user: User | None,
    limit: int,
    offset: int,
) -> ScalarResult[Comment]:
    """Return comments for given content"""

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
            Comment.created > round_datetime(utcnow(), hours=1),
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

    # Update comments count here
    content = await get_content_by_id(
        session, comment.content_type, comment.content_id
    )

    content.comments_count = await get_comments_count(
        session, comment.content_type, content
    )

    content.comments_count_pagination = await get_comments_count(
        session, comment.content_type, content, True
    )

    session.add(content)
    await session.commit()

    await create_log(
        session,
        constants.LOG_COMMENT_HIDE,
        user,
        comment.id,
        {"content_type": comment.content_type},
    )

    return True


async def latest_comments(session: AsyncSession):
    comments = await session.scalars(
        select(Comment)
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

    return comments


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


async def get_comments(
    session: AsyncSession,
    request_user: User | None,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(Comment)
        .filter(
            func.nlevel(Comment.path) == 1,
            Comment.hidden == False,  # noqa: E712
            Comment.private == False,  # noqa: E712
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
        .order_by(desc(Comment.created))
        .limit(limit)
        .offset(offset)
    )


# NOTE: I still hate this function but less than before.
# NOTE: This code is a liability. It must be updated when
# new identities added for Comment or Edit
async def generate_preview(
    session: AsyncSession,
    original_comment: Comment,
):
    comment = await session.scalar(
        select(Comment)
        .filter(Comment.id == original_comment.id)
        .options(immediateload(CollectionComment.content))
        .options(immediateload(ArticleComment.content))
        .options(immediateload(AnimeComment.content))
        .options(immediateload(MangaComment.content))
        .options(immediateload(NovelComment.content))
        .options(immediateload(EditComment.content))
        .order_by(desc(Comment.created))
    )

    title = None
    slug = comment.content.slug
    image = None

    if isinstance(comment, AnimeComment):
        image = comment.content.image
        title = (
            comment.content.title_ua
            or comment.content.title_en
            or comment.content.title_ja
        )

    if isinstance(comment, MangaComment) or isinstance(comment, NovelComment):
        image = comment.content.image
        title = (
            comment.content.title_ua
            or comment.content.title_en
            or comment.content.title_original
        )

    if isinstance(comment, ArticleComment):
        title = comment.content.title

    if isinstance(comment, EditComment):
        # This is horrible hack, but we need this to prevent SQLAlchemy bug
        # For some reason edit content is not loaded sometimes
        await session.refresh(comment.content)

        edit = await session.scalar(
            select(Edit)
            .filter(Edit.id == comment.content_id)
            .options(
                joinedload(AnimeEdit.content).joinedload(Anime.image_relation),
                joinedload(MangaEdit.content).joinedload(Manga.image_relation),
                joinedload(NovelEdit.content).joinedload(Novel.image_relation),
                joinedload(CharacterEdit.content).joinedload(
                    Character.image_relation
                ),
                joinedload(PersonEdit.content).joinedload(
                    Person.image_relation
                ),
            )
        )

        if edit:
            image = (
                edit.content.image
                if isinstance(comment.content.content, Anime)
                else edit.content.image
            )

    if isinstance(comment, CollectionComment):
        collection_content = await session.scalar(
            select(CollectionContent)
            .filter(CollectionContent.collection == comment.content)
            .order_by(asc(CollectionContent.order))
            .limit(1)
        )

        content = collection_content.content

        image = (
            content.image
            if comment.content.content_type == constants.CONTENT_ANIME
            else content.image
        )

        title = collection_content.collection.title

    original_comment.preview = {
        "image": image,
        "slug": slug,
        "title": title,
    }

    session.add(original_comment)
    await session.commit()

    return original_comment
