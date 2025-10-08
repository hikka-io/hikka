from sqlalchemy import select, asc, desc, func, ScalarResult
from app.models.list.read import MangaRead, NovelRead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.sql.selectable import Select
from app.utils import round_datetime
from sqlalchemy.orm import joinedload
from .utils import calculate_before
from app.utils import utcnow
from app.models import Log
from app import constants
import copy

from app.service import (
    get_user_by_username,
    get_content_by_slug,
    create_log,
)

from .schemas import (
    EditContentToDoEnum,
    EditContentTypeEnum,
    ContentToDoEnum,
    EditSearchArgs,
    EditArgs,
)

from app.models import (
    UserEditStats,
    CharacterEdit,
    AnimeWatch,
    PersonEdit,
    AnimeEdit,
    MangaEdit,
    NovelEdit,
    Character,
    Person,
    Anime,
    Manga,
    Novel,
    Genre,
    Edit,
    User,
)


content_type_to_edit_class = {
    constants.CONTENT_CHARACTER: CharacterEdit,
    constants.CONTENT_PERSON: PersonEdit,
    constants.CONTENT_ANIME: AnimeEdit,
    constants.CONTENT_MANGA: MangaEdit,
    constants.CONTENT_NOVEL: NovelEdit,
}


async def update_edit_stats(session: AsyncSession, edit: Edit):
    if not (
        stats := await session.scalar(
            select(UserEditStats).filter(UserEditStats.user == edit.author)
        )
    ):
        stats = UserEditStats(
            **{"user": edit.author, "accepted": 0, "closed": 0, "denied": 0}
        )

    edits_count = await session.scalar(
        select(func.count(Edit.id)).filter(
            Edit.author == edit.author, Edit.status == edit.status
        )
    )

    setattr(stats, edit.status, edits_count)
    session.add(stats)
    await session.commit()

    return stats


async def get_edit(session: AsyncSession, edit_id: int) -> Edit | None:
    """Return Edit by edit_id"""

    return await session.scalar(
        select(Edit)
        .filter(Edit.edit_id == edit_id)
        .options(
            joinedload(CharacterEdit.content),
            joinedload(PersonEdit.content),
            joinedload(AnimeEdit.content),
            joinedload(MangaEdit.content),
            joinedload(NovelEdit.content),
        )
    )


def build_edit_order_by(sort: list[str]):
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

    if args.content_type:
        query = query.filter(Edit.content_type == args.content_type)

    if args.slug:
        content = await get_content_by_slug(
            session, args.content_type, args.slug
        )

        query = query.filter(Edit.content_id == content.id)

    if args.status:
        query = query.filter(Edit.status == args.status)

    query = query.filter(
        Edit.system_edit == False,  # noqa: E712
        Edit.hidden == False,  # noqa: E712
    )

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
) -> ScalarResult[Edit]:
    """Return all edits"""

    query = await edits_search_filter(session, args, select(Edit))

    query = query.options(
        joinedload(AnimeEdit.content).load_only(
            Anime.title_ja,
            Anime.title_en,
            Anime.title_ua,
            Anime.slug,
        ),
        joinedload(MangaEdit.content).load_only(
            Manga.title_original,
            Manga.title_en,
            Manga.title_ua,
            Manga.slug,
        ),
        joinedload(NovelEdit.content).load_only(
            Novel.title_original,
            Novel.title_en,
            Novel.title_ua,
            Novel.slug,
        ),
        joinedload(PersonEdit.content).load_only(
            Person.name_native,
            Person.name_en,
            Person.name_ua,
            Person.slug,
        ),
        joinedload(CharacterEdit.content).load_only(
            Character.name_ja,
            Character.name_en,
            Character.name_ua,
            Character.slug,
        ),
    )

    query = query.order_by(*build_edit_order_by(args.sort))
    query = query.limit(limit).offset(offset)

    return await session.scalars(query)


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
    edit.updated = utcnow()
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

    # If user marked edit as auto accept we should do that
    if args.auto:
        await accept_pending_edit(
            session, edit, user, constants.LOG_EDIT_UPDATE_ACCEPT_AUTO
        )

    return edit


async def close_pending_edit(
    session: AsyncSession,
    edit: Edit,
) -> Edit:
    """Close pending edit"""

    edit.status = constants.EDIT_CLOSED
    edit.updated = utcnow()

    session.add(edit)
    await session.commit()

    await create_log(
        session,
        constants.LOG_EDIT_CLOSE,
        edit.author,
        edit.id,
    )

    await update_edit_stats(session, edit)

    return edit


async def accept_pending_edit(
    session: AsyncSession,
    edit: Edit,
    moderator: User,
    log_type: str = constants.LOG_EDIT_ACCEPT,
) -> Edit:
    """Accept pending edit"""

    content = edit.content

    # Fix for SQLAlchemy shenanigans
    if hasattr(content, "ignored_fields"):
        content.ignored_fields = copy.deepcopy(content.ignored_fields)

    # We recalculate before here because field may have changed
    # Just in case, let's hope it won't happen on production
    # TODO: find better way to handle this behaviour
    before = {}

    if "genres" in edit.after:
        new_genre_slugs = edit.after.pop("genres")
        
        before["genres"] = [genre.slug for genre in content.genres]
        
        new_genres = await session.scalars(
            select(Genre).filter(Genre.slug.in_(new_genre_slugs))
        )
        
        # Replace the relationship list. SQLAlchemy handles the M2M update.
        content.genres = new_genres.all()
        
        # Add 'genres' to ignored_fields to prevent aggregator overwrites
        if hasattr(content, "ignored_fields"):
            if "genres" not in content.ignored_fields:
                content.ignored_fields.append("genres")

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
    edit.moderator = moderator
    edit.updated = utcnow()
    edit.before = before

    session.add(edit)
    session.add(content)
    await session.commit()

    await create_log(
        session,
        log_type,
        moderator,
        edit.id,
    )

    await update_edit_stats(session, edit)

    return edit


async def create_pending_edit(
    session: AsyncSession,
    content_type: EditContentTypeEnum,
    content: Person | Anime | Character,
    args: EditArgs,
    author: User,
) -> AnimeEdit:
    """Create edit for given content with pending status"""

    edit_model = content_type_to_edit_class[content_type]

    before = calculate_before(content, args.after)

    now = utcnow()

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
        await accept_pending_edit(
            session, edit, author, constants.LOG_EDIT_ACCEPT_AUTO
        )

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
    edit.moderator = moderator
    edit.updated = utcnow()

    session.add(edit)
    await session.commit()

    await create_log(
        session,
        constants.LOG_EDIT_DENY,
        moderator,
        edit.id,
    )

    await update_edit_stats(session, edit)

    return edit


async def content_todo_total(
    session: AsyncSession,
    content_type: EditContentToDoEnum,
    todo_type: ContentToDoEnum,
):
    match content_type:
        case constants.CONTENT_ANIME:
            content_type = Anime
        case constants.CONTENT_MANGA:
            content_type = Manga
        case constants.CONTENT_NOVEL:
            content_type = Novel

    query = select(func.count(content_type.id)).filter(
        ~content_type.media_type.in_([constants.MEDIA_TYPE_MUSIC]),
        content_type.deleted == False,  # noqa: E712
    )

    if todo_type == constants.TODO_TITLE_UA:
        query = query.filter(content_type.title_ua == None)  # noqa: E711

    if todo_type == constants.TODO_SYNOPSIS_UA:
        query = query.filter(content_type.synopsis_ua == None)  # noqa: E711

    return await session.scalar(query)


async def content_todo(
    session: AsyncSession,
    content_type: EditContentToDoEnum,
    todo_type: ContentToDoEnum,
    request_user: User | None,
    limit: int,
    offset: int,
):
    match content_type:
        case constants.CONTENT_ANIME:
            content_type = Anime
            option = AnimeWatch
        case constants.CONTENT_MANGA:
            content_type = Manga
            option = MangaRead
        case constants.CONTENT_NOVEL:
            content_type = Novel
            option = NovelRead

    # Load request user watch statuses here
    load_options = [
        joinedload(
            content_type.read if content_type != Anime else content_type.watch
        ),
        with_loader_criteria(
            option,
            option.user_id == request_user.id if request_user else None,
        ),
    ]

    query = select(content_type).filter(
        ~content_type.media_type.in_([constants.MEDIA_TYPE_MUSIC]),
        content_type.deleted == False,  # noqa: E712
    )

    if todo_type == constants.TODO_TITLE_UA:
        query = query.filter(content_type.title_ua == None)  # noqa: E711

    if todo_type == constants.TODO_SYNOPSIS_UA:
        query = query.filter(content_type.synopsis_ua == None)  # noqa: E711

    return await session.scalars(
        query.order_by(
            desc(content_type.score),
            desc(content_type.scored_by),
            desc(content_type.content_id),
        )
        .options(*load_options)
        .limit(limit)
        .offset(offset)
    )


async def count_created_edit_limit(session: AsyncSession, user: User) -> int:
    return await session.scalar(
        select(func.count())
        .filter(
            Log.log_type.in_(
                [
                    constants.LOG_EDIT_CREATE,
                ]
            )
        )
        .filter(Log.created > round_datetime(utcnow(), minutes=5))
        .filter(Log.user == user)
    )


async def count_update_edit_limit(session: AsyncSession, user: User) -> int:
    return await session.scalar(
        select(func.count())
        .filter(
            Log.log_type.in_(
                [
                    constants.LOG_EDIT_UPDATE,
                ]
            )
        )
        .filter(Log.created > round_datetime(utcnow(), minutes=5))
        .filter(Log.user == user)
    )
