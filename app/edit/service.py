from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import with_expression
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from .utils import calculate_before
from datetime import datetime
from app import constants

from app.service import (
    get_comments_count_subquery,
    get_user_by_username,
    get_content_by_slug,
    create_log,
)

from .schemas import (
    ContentTypeEnum,
    EditSearchArgs,
    AnimeToDoEnum,
    EditArgs,
)

from app.models import (
    CharacterEdit,
    AnimeWatch,
    PersonEdit,
    AnimeEdit,
    Character,
    Person,
    Anime,
    Edit,
    User,
)


content_type_to_edit_class = {
    constants.CONTENT_CHARACTER: CharacterEdit,
    constants.CONTENT_PERSON: PersonEdit,
    constants.CONTENT_ANIME: AnimeEdit,
}


async def get_edit(session: AsyncSession, edit_id: int) -> Edit | None:
    """Return Edit by edit_id"""

    return await session.scalar(
        select(Edit)
        .filter(Edit.edit_id == edit_id)
        .options(
            with_expression(
                Edit.comments_count,
                get_comments_count_subquery(
                    Edit.id, constants.CONTENT_SYSTEM_EDIT
                ),
            )
        )
    )


async def count_edits_by_content_id(
    session: AsyncSession, content_id: str
) -> int:
    """Count edits for given content"""

    return await session.scalar(
        select(func.count(Edit.id)).filter(Edit.content_id == content_id)
    )


async def get_edits_by_content_id(
    session: AsyncSession,
    content_id: str,
    limit: int,
    offset: int,
) -> list[Edit]:
    """Return edits for given content"""

    return await session.scalars(
        select(Edit)
        .filter(Edit.content_id == content_id)
        .order_by(desc(Edit.edit_id))
        .options(
            with_expression(
                Edit.comments_count,
                get_comments_count_subquery(
                    Edit.id, constants.CONTENT_SYSTEM_EDIT
                ),
            )
        )
        .limit(limit)
        .offset(offset)
    )


def build_order_by(sort: list[str]):
    order_mapping = {
        "edit_id": Edit.edit_id,
        "created": Edit.created,
    }

    order_by = [
        (
            desc(order_mapping[field])
            if order == "desc"
            else asc(order_mapping[field])
        )
        for field, order in (entry.split(":") for entry in sort)
    ]

    return order_by


async def edits_search_filter(
    session: AsyncSession,
    args: EditSearchArgs,
    query: Select,
):
    if args.author:
        author = await get_user_by_username(session, args.author)
        query = query.filter(Edit.author == author)

    if args.moderator:
        moderator = await get_user_by_username(session, args.moderator)
        query = query.filter(Edit.moderator == moderator)

    if args.content:
        content = await get_content_by_slug(
            session, args.content.content_type, args.content.slug
        )

        query = query.filter(Edit.content_id == content.id)

    if args.status:
        query = query.filter(Edit.status == args.status)

    query = query.filter(
        Edit.system_edit == False, Edit.hidden == False  # noqa: E712
    )

    # query = query.order_by(*build_order_by(search.sort))

    return query


async def count_edits(session: AsyncSession, args: EditSearchArgs) -> int:
    """Count edits"""

    query = await edits_search_filter(
        session, args, select(func.count(Edit.id))
    )

    return await session.scalar(query)


async def get_edits(
    session: AsyncSession,
    args: EditSearchArgs,
    limit: int,
    offset: int,
) -> list[Edit]:
    """Return all edits"""

    query = await edits_search_filter(session, args, select(Edit))

    query = query.options(
        with_expression(
            Edit.comments_count,
            get_comments_count_subquery(Edit.id, constants.CONTENT_SYSTEM_EDIT),
        )
    )

    query = query.order_by(*build_order_by(args.sort))
    query = query.limit(limit).offset(offset)

    return await session.scalars(query)


async def count_edits_legacy(session: AsyncSession) -> int:
    """Count all (non system) edits"""

    return await session.scalar(
        select(func.count(Edit.id)).filter(
            Edit.system_edit == False, Edit.hidden == False  # noqa: E712
        )
    )


async def get_edits_legacy(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> list[Edit]:
    """Return all edits"""

    return await session.scalars(
        select(Edit)
        .filter(Edit.system_edit == False, Edit.hidden == False)  # noqa: E712
        .order_by(desc(Edit.edit_id))
        .options(
            with_expression(
                Edit.comments_count,
                get_comments_count_subquery(
                    Edit.id, constants.CONTENT_SYSTEM_EDIT
                ),
            )
        )
        .limit(limit)
        .offset(offset)
    )


async def update_pending_edit(
    session: AsyncSession,
    edit: Edit,
    user: User,
    args: EditArgs,
) -> Edit:
    """Update pending edit"""

    old_edit = {
        "description": edit.description,
        "after": edit.after,
    }

    edit.before = calculate_before(edit.content, args.after)
    edit.description = args.description
    edit.updated = datetime.now()
    edit.after = args.after

    updated_edit = {
        "description": edit.description,
        "after": edit.after,
    }

    session.add(edit)
    await session.commit()

    await create_log(
        session,
        constants.LOG_EDIT_UPDATE,
        user,
        edit.id,
        {
            "updated_edit": updated_edit,
            "old_edit": old_edit,
        },
    )

    return edit


async def close_pending_edit(
    session: AsyncSession,
    edit: Edit,
) -> Edit:
    """Close pending edit"""

    edit.status = constants.EDIT_CLOSED
    edit.updated = datetime.now()

    session.add(edit)
    await session.commit()

    await create_log(
        session,
        constants.LOG_EDIT_CLOSE,
        edit.author,
        edit.id,
    )

    return edit


async def accept_pending_edit(
    session: AsyncSession,
    edit: Edit,
    moderator: User,
    auto: bool = False,
) -> Edit:
    """Accept pending edit"""

    content = edit.content

    # We recalculate before here because field may have changed
    # Just in case, let's hope it won't happen on production
    # ToDo: find better way to handle this behaviour
    before = {}

    for key, value in edit.after.items():
        before[key] = getattr(content, key)
        setattr(content, key, value)

        if hasattr(content, "ignored_fields"):
            if key not in content.ignored_fields:
                content.ignored_fields.append(key)

    # Make sure content is marked to be updated in Meilisearch
    if hasattr(content, "needs_search_update"):
        content.needs_search_update = True

    edit.status = constants.EDIT_ACCEPTED
    edit.updated = datetime.now()
    edit.moderator = moderator
    edit.before = before

    session.add(edit)
    session.add(content)
    await session.commit()

    await create_log(
        session,
        constants.LOG_EDIT_ACCEPT_AUTO if auto else constants.LOG_EDIT_ACCEPT,
        moderator,
        edit.id,
    )

    return edit


async def create_pending_edit(
    session: AsyncSession,
    content_type: ContentTypeEnum,
    content: Person | Anime | Character,
    args: EditArgs,
    author: User,
) -> AnimeEdit:
    """Create edit for given content with pending status"""

    edit_model = content_type_to_edit_class[content_type]

    before = calculate_before(content, args.after)

    now = datetime.utcnow()

    edit = edit_model(
        **{
            "status": constants.EDIT_PENDING,
            "description": args.description,
            "content_type": content_type,
            "content_id": content.id,
            "after": args.after,
            "author": author,
            "before": before,
            "created": now,
            "updated": now,
        }
    )

    session.add(edit)
    await session.commit()

    # If user marked edit as auto accept we should do that
    if args.auto:
        await session.refresh(edit)
        await accept_pending_edit(session, edit, author, True)

    else:
        await create_log(
            session,
            constants.LOG_EDIT_CREATE,
            author,
            edit.id,
        )

    # This step is needed to load content relation for slug
    await session.refresh(edit)

    return edit


async def deny_pending_edit(
    session: AsyncSession,
    edit: Edit,
    moderator: User,
) -> Edit:
    """Deny pending edit"""

    edit.status = constants.EDIT_DENIED
    edit.updated = datetime.now()
    edit.moderator = moderator

    session.add(edit)
    await session.commit()

    await create_log(
        session,
        constants.LOG_EDIT_DENY,
        moderator,
        edit.id,
    )

    return edit


async def anime_todo_total(
    session: AsyncSession,
    todo_type: AnimeToDoEnum,
):
    query = select(func.count(Anime.id)).filter(
        ~Anime.media_type.in_([constants.MEDIA_TYPE_MUSIC])
    )

    if todo_type == constants.TODO_ANIME_TITLE_UA:
        query = query.filter(Anime.title_ua == None)  # noqa: E711

    if todo_type == constants.TODO_ANIME_SYNOPSIS_UA:
        query = query.filter(Anime.synopsis_ua == None)  # noqa: E711

    return await session.scalar(query)


async def anime_todo(
    session: AsyncSession,
    todo_type: AnimeToDoEnum,
    request_user: User | None,
    limit: int,
    offset: int,
):
    # Load request user watch statuses here
    load_options = [
        joinedload(Anime.watch),
        with_loader_criteria(
            AnimeWatch,
            AnimeWatch.user_id == request_user.id if request_user else None,
        ),
    ]

    query = select(Anime).filter(
        ~Anime.media_type.in_([constants.MEDIA_TYPE_MUSIC])
    )

    if todo_type == constants.TODO_ANIME_TITLE_UA:
        query = query.filter(Anime.title_ua == None)  # noqa: E711

    if todo_type == constants.TODO_ANIME_SYNOPSIS_UA:
        query = query.filter(Anime.synopsis_ua == None)  # noqa: E711

    return await session.scalars(
        query.order_by(
            desc(Anime.score), desc(Anime.scored_by), desc(Anime.content_id)
        )
        .options(*load_options)
        .limit(limit)
        .offset(offset)
    )
