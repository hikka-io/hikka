from app.models.list.read import MangaRead, NovelRead
from app.common.service.sort import build_order_by
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import joinedload
from app.utils import round_datetime
from .utils import calculate_before
from app.utils import utcnow
from app.models import Log
from app import constants
import copy

from sqlalchemy import (
    ScalarResult,
    select,
    desc,
    func,
    and_,
    asc,
    or_,
)

from app.service import (
    get_user_by_username,
    get_content_by_slug,
    create_log,
)

from .schemas import (
    EditContentToDoEnum,
    EditContentTypeEnum,
    CharacterTodoArgs,
    ContentToDoEnum,
    EditSearchArgs,
    PersonTodoArgs,
    AnimeTodoArgs,
    MangaTodoArgs,
    NovelTodoArgs,
    EditArgs,
)

from app.models import (
    AnimeCharacter,
    MangaCharacter,
    NovelCharacter,
    UserEditStats,
    CharacterEdit,
    MangaAuthor,
    NovelAuthor,
    AnimeWatch,
    PersonEdit,
    AnimeStaff,
    AnimeEdit,
    MangaEdit,
    NovelEdit,
    Character,
    Company,
    Magazine,
    Person,
    Genre,
    Anime,
    Manga,
    Novel,
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


# This would introduce some headache in the future
# But this is proble for future me
# TODO: system edits currently don't have preview
# since we don't show them
def generate_content_preview(content_type: str, content) -> dict:
    match content_type:
        case constants.CONTENT_ANIME:
            return {
                "title_ja": content.title_ja,
                "title_en": content.title_en,
                "title_ua": content.title_ua,
                "slug": content.slug,
            }

        case constants.CONTENT_MANGA | constants.CONTENT_NOVEL:
            return {
                "title_original": content.title_original,
                "title_en": content.title_en,
                "title_ua": content.title_ua,
                "slug": content.slug,
            }

        case constants.CONTENT_PERSON:
            return {
                "name_ja": content.name_native,
                "name_en": content.name_en,
                "name_ua": content.name_ua,
                "slug": content.slug,
            }

        case constants.CONTENT_CHARACTER:
            return {
                "name_ja": content.name_ja,
                "name_en": content.name_en,
                "name_ua": content.name_ua,
                "slug": content.slug,
            }

        case _:
            return {}


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

    edit.content_preview = generate_content_preview(
        edit.content_type,
        content,
    )

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

    edit.content_preview = generate_content_preview(
        content_type,
        content,
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


async def get_todo_anime_list(
    session: AsyncSession,
    limit: int,
    offset: int,
    search: AnimeTodoArgs,
    filter_ids: list[str],
) -> tuple[int, ScalarResult[Anime]]:
    and_filters, or_filters = todo_anime_filters(search)
    filters = [*and_filters]

    if filter_ids:
        filters.append(Anime.content_id.in_(filter_ids))

    if or_filters:
        filters.append(or_(*or_filters))

    total = await session.scalar(
        select(func.count(Anime.id)).filter(*filters)
    )

    if not total:
        return 0, []

    data = await session.scalars(
        select(Anime)
        .filter(*filters)
        .order_by(
            *build_order_by(
                search.sort,
                order_mapping={
                    "title_original": Anime.title_ja,
                    "title_ua": Anime.title_ua,
                    "title_en": Anime.title_en,
                    "start_date": Anime.start_date,
                    "media_type": Anime.media_type,
                },
                tiebreaker=asc(Anime.id),
                nullable=[
                    "title_ua",
                    "title_en",
                    "title_original",
                    "start_date",
                ],
            )
        )
        .limit(limit)
        .offset(offset)
    )

    return total, data


def todo_anime_filters(search: AnimeTodoArgs) -> tuple[list, list]:
    and_filters = [Anime.deleted == False]
    or_filters = []

    if search.media_type:
        and_filters.append(Anime.media_type.in_(search.media_type))
    else:
        # Exclude music by default for backward compatibility with the
        # previous API endpoint @router.get("/todo/{content_type}/{todo_type}")
        # NOTE: Probably redundant, need check with the moderation team
        and_filters.append(~Anime.media_type.in_([constants.MEDIA_TYPE_MUSIC]))

    if search.mal_id is not None:
        and_filters.append(Anime.mal_id == search.mal_id)

    todo_field_columns = {
        "title_ua": Anime.title_ua,
        "title_en": Anime.title_en,
        "title_original": Anime.title_ja,
        "synopsis_ua": Anime.synopsis_ua,
        "synopsis_en": Anime.synopsis_en,
    }

    for entry in search.fields:
        negative = entry.startswith("-")
        column = todo_field_columns[entry[1:] if negative else entry]
        and_filters.append(
            and_(column != None, column != "")  # noqa: E711
            if negative
            else or_(column == None, column == "")  # noqa: E711
        )

    if not search.fields:
        or_filters = [
            or_(Anime.title_ua == None, Anime.title_ua == ""),          # noqa: E711
            or_(Anime.title_en == None, Anime.title_en == ""),          # noqa: E711
            or_(Anime.title_ja == None, Anime.title_ja == ""),          # noqa: E711
            or_(Anime.synopsis_ua == None, Anime.synopsis_ua == ""),    # noqa: E711
            or_(Anime.synopsis_en == None, Anime.synopsis_en == ""),    # noqa: E711
        ]

    if search.status:
        and_filters.append(Anime.status.in_(search.status))

    if search.rating:
        and_filters.append(Anime.rating.in_(search.rating))

    if search.season:
        and_filters.append(Anime.season.in_(search.season))

    if search.years[0] is not None:
        and_filters.append(Anime.year >= search.years[0])

    if search.years[1] is not None:
        and_filters.append(Anime.year <= search.years[1])

    if search.genres:
        include_genres = []
        exclude_genres = []

        for genre_slug in search.genres:
            if genre_slug.startswith("-"):
                exclude_genres.append(genre_slug[1:])
            else:
                include_genres.append(genre_slug)

        if include_genres:
            and_filters.append(
                and_(
                    *[
                        Anime.genres.any(Genre.slug == slug)
                        for slug in include_genres
                    ]
                )
            )

        if exclude_genres:
            and_filters.append(
                and_(
                    *[
                        ~Anime.genres.any(Genre.slug == slug)
                        for slug in exclude_genres
                    ]
                )
            )

    if search.studios:
        and_filters.append(Anime.studios.any(Company.slug.in_(search.studios)))

    return and_filters, or_filters


async def get_todo_manga_list(
    session: AsyncSession,
    limit: int,
    offset: int,
    search: MangaTodoArgs,
    filter_ids: list[str],
) -> tuple[int, ScalarResult[Manga]]:
    and_filters, or_filters = todo_manga_filters(search)
    filters = [*and_filters]

    if filter_ids:
        filters.append(Manga.content_id.in_(filter_ids))

    if or_filters:
        filters.append(or_(*or_filters))

    total = await session.scalar(
        select(func.count(Manga.id)).filter(*filters)
    )

    if not total:
        return 0, []

    data = await session.scalars(
        select(Manga)
        .filter(*filters)
        .order_by(
            *build_order_by(
                search.sort,
                order_mapping={
                    "title_original": Manga.title_original,
                    "title_ua": Manga.title_ua,
                    "title_en": Manga.title_en,
                    "start_date": Manga.start_date,
                    "media_type": Manga.media_type,
                },
                tiebreaker=asc(Manga.id),
                nullable=[
                    "title_ua",
                    "title_en",
                    "title_original",
                    "start_date",
                ],
            )
        )
        .limit(limit)
        .offset(offset)
    )

    return total, data


def todo_manga_filters(search: MangaTodoArgs) -> tuple[list, list]:
    and_filters = [Manga.deleted == False]
    or_filters = []

    if search.media_type:
        and_filters.append(Manga.media_type.in_(search.media_type))

    if search.mal_id is not None:
        and_filters.append(Manga.mal_id == search.mal_id)

    todo_field_columns = {
        "title_ua": Manga.title_ua,
        "title_en": Manga.title_en,
        "title_original": Manga.title_original,
        "synopsis_ua": Manga.synopsis_ua,
        "synopsis_en": Manga.synopsis_en,
    }

    for entry in search.fields:
        negative = entry.startswith("-")
        column = todo_field_columns[entry[1:] if negative else entry]
        and_filters.append(
            and_(column != None, column != "")  # noqa: E711
            if negative
            else or_(column == None, column == "")  # noqa: E711
        )

    if not search.fields:
        or_filters = [
            or_(Manga.title_ua == None, Manga.title_ua == ""),                # noqa: E711
            or_(Manga.title_en == None, Manga.title_en == ""),                # noqa: E711
            or_(Manga.title_original == None, Manga.title_original == ""),    # noqa: E711
            or_(Manga.synopsis_ua == None, Manga.synopsis_ua == ""),          # noqa: E711
            or_(Manga.synopsis_en == None, Manga.synopsis_en == ""),          # noqa: E711
        ]

    if search.status:
        and_filters.append(Manga.status.in_(search.status))

    if search.years[0] is not None:
        and_filters.append(Manga.year >= search.years[0])

    if search.years[1] is not None:
        and_filters.append(Manga.year <= search.years[1])

    if search.genres:
        include_genres = []
        exclude_genres = []

        for genre_slug in search.genres:
            if genre_slug.startswith("-"):
                exclude_genres.append(genre_slug[1:])
            else:
                include_genres.append(genre_slug)

        if include_genres:
            and_filters.append(
                and_(
                    *[
                        Manga.genres.any(Genre.slug == slug)
                        for slug in include_genres
                    ]
                )
            )

        if exclude_genres:
            and_filters.append(
                and_(
                    *[
                        ~Manga.genres.any(Genre.slug == slug)
                        for slug in exclude_genres
                    ]
                )
            )

    if search.magazines:
        and_filters.append(
            Manga.magazines.any(Magazine.slug.in_(search.magazines))
        )

    return and_filters, or_filters


async def get_todo_novel_list(
    session: AsyncSession,
    limit: int,
    offset: int,
    search: NovelTodoArgs,
    filter_ids: list[str],
) -> tuple[int, ScalarResult[Novel]]:
    and_filters, or_filters = todo_novel_filters(search)
    filters = [*and_filters]

    if filter_ids:
        filters.append(Novel.content_id.in_(filter_ids))

    if or_filters:
        filters.append(or_(*or_filters))

    total = await session.scalar(
        select(func.count(Novel.id)).filter(*filters)
    )

    if not total:
        return 0, []

    data = await session.scalars(
        select(Novel)
        .filter(*filters)
        .order_by(
            *build_order_by(
                search.sort,
                order_mapping={
                    "title_original": Novel.title_original,
                    "title_ua": Novel.title_ua,
                    "title_en": Novel.title_en,
                    "start_date": Novel.start_date,
                    "media_type": Novel.media_type,
                },
                tiebreaker=asc(Novel.id),
                nullable=[
                    "title_ua",
                    "title_en",
                    "title_original",
                    "start_date",
                ],
            )
        )
        .limit(limit)
        .offset(offset)
    )

    return total, data


def todo_novel_filters(search: NovelTodoArgs) -> tuple[list, list]:
    and_filters = [Novel.deleted == False]
    or_filters = []

    if search.media_type:
        and_filters.append(Novel.media_type.in_(search.media_type))

    if search.mal_id is not None:
        and_filters.append(Novel.mal_id == search.mal_id)

    todo_field_columns = {
        "title_ua": Novel.title_ua,
        "title_en": Novel.title_en,
        "title_original": Novel.title_original,
        "synopsis_ua": Novel.synopsis_ua,
        "synopsis_en": Novel.synopsis_en,
    }

    for entry in search.fields:
        negative = entry.startswith("-")
        column = todo_field_columns[entry[1:] if negative else entry]
        and_filters.append(
            and_(column != None, column != "")  # noqa: E711
            if negative
            else or_(column == None, column == "")  # noqa: E711
        )

    if not search.fields:
        or_filters = [
            or_(Novel.title_ua == None, Novel.title_ua == ""),                # noqa: E711
            or_(Novel.title_en == None, Novel.title_en == ""),                # noqa: E711
            or_(Novel.title_original == None, Novel.title_original == ""),    # noqa: E711
            or_(Novel.synopsis_ua == None, Novel.synopsis_ua == ""),          # noqa: E711
            or_(Novel.synopsis_en == None, Novel.synopsis_en == ""),          # noqa: E711
        ]

    if search.status:
        and_filters.append(Novel.status.in_(search.status))

    if search.years[0] is not None:
        and_filters.append(Novel.year >= search.years[0])

    if search.years[1] is not None:
        and_filters.append(Novel.year <= search.years[1])

    if search.genres:
        include_genres = []
        exclude_genres = []

        for genre_slug in search.genres:
            if genre_slug.startswith("-"):
                exclude_genres.append(genre_slug[1:])
            else:
                include_genres.append(genre_slug)

        if include_genres:
            and_filters.append(
                and_(
                    *[
                        Novel.genres.any(Genre.slug == slug)
                        for slug in include_genres
                    ]
                )
            )

        if exclude_genres:
            and_filters.append(
                and_(
                    *[
                        ~Novel.genres.any(Genre.slug == slug)
                        for slug in exclude_genres
                    ]
                )
            )

    if search.magazines:
        and_filters.append(
            Novel.magazines.any(Magazine.slug.in_(search.magazines))
        )

    return and_filters, or_filters


async def get_todo_character_list(
    session: AsyncSession,
    limit: int,
    offset: int,
    search: CharacterTodoArgs,
    filter_slugs: list[str],
) -> tuple[int, ScalarResult[Character]]:
    and_filters, or_filters = todo_character_filters(search)
    filters = [*and_filters]

    if filter_slugs:
        filters.append(Character.slug.in_(filter_slugs))

    if or_filters:
        filters.append(or_(*or_filters))

    count_query = select(func.count(Character.id))
    query = select(Character)

    if search.content_type and search.content_slug:
        content_joins = {
            EditContentToDoEnum.content_anime: (
                AnimeCharacter,
                AnimeCharacter.anime_id,
                Anime,
            ),
            EditContentToDoEnum.content_manga: (
                MangaCharacter,
                MangaCharacter.manga_id,
                Manga,
            ),
            EditContentToDoEnum.content_novel: (
                NovelCharacter,
                NovelCharacter.novel_id,
                Novel,
            ),
        }
        model, column, content_model = content_joins[search.content_type]
        content_id_subquery = (
            select(content_model.id)
            .filter(content_model.slug == search.content_slug)
            .scalar_subquery()
        )
        join_condition = and_(
            model.character_id == Character.id, column == content_id_subquery
        )

        count_query = count_query.join(model, join_condition)
        query = query.join(model, join_condition)

    total = await session.scalar(count_query.filter(*filters))

    if not total:
        return 0, []

    data = await session.scalars(
        query.filter(*filters)
        .order_by(
            *build_order_by(
                search.sort,
                order_mapping={
                    "name_original": Character.name_ja,
                    "name_ua": Character.name_ua,
                    "name_en": Character.name_en,
                },
                tiebreaker=asc(Character.id),
                nullable=["name_ua", "name_en", "name_original"],
            )
        )
        .limit(limit)
        .offset(offset)
    )

    return total, data


def todo_character_filters(search: CharacterTodoArgs) -> tuple[list, list]:
    and_filters, or_filters = [], []

    todo_field_columns = {
        "name_ua": Character.name_ua,
        "name_en": Character.name_en,
        "name_original": Character.name_ja,
        "description_ua": Character.description_ua,
    }

    for entry in search.fields:
        negative = entry.startswith("-")
        column = todo_field_columns[entry[1:] if negative else entry]
        and_filters.append(
            and_(column != None, column != "")  # noqa: E711
            if negative
            else or_(column == None, column == "")  # noqa: E711
        )

    if not search.fields:
        or_filters = [
            or_(Character.name_ua == None, Character.name_ua == ""),                  # noqa: E711
            or_(Character.name_en == None, Character.name_en == ""),                  # noqa: E711
            or_(Character.name_ja == None, Character.name_ja == ""),                  # noqa: E711
            or_(Character.description_ua == None, Character.description_ua == ""),    # noqa: E711
        ]

    return and_filters, or_filters


async def get_todo_person_list(
    session: AsyncSession,
    limit: int,
    offset: int,
    search: PersonTodoArgs,
    filter_slugs: list[str],
) -> tuple[int, ScalarResult[Person]]:
    and_filters, or_filters = todo_person_filters(search)
    filters = [*and_filters]

    if filter_slugs:
        filters.append(Person.slug.in_(filter_slugs))

    if or_filters:
        filters.append(or_(*or_filters))

    count_query = select(func.count(Person.id))
    query = select(Person)

    if search.content_type and search.content_slug:
        content_joins = {
            EditContentToDoEnum.content_anime: (
                AnimeStaff,
                AnimeStaff.anime_id,
                Anime,
            ),
            EditContentToDoEnum.content_manga: (
                MangaAuthor,
                MangaAuthor.manga_id,
                Manga,
            ),
            EditContentToDoEnum.content_novel: (
                NovelAuthor,
                NovelAuthor.novel_id,
                Novel,
            ),
        }
        model, column, content_model = content_joins[search.content_type]
        content_id_subquery = (
            select(content_model.id)
            .filter(content_model.slug == search.content_slug)
            .scalar_subquery()
        )
        join_condition = and_(
            model.person_id == Person.id, column == content_id_subquery
        )

        count_query = count_query.join(model, join_condition)
        query = query.join(model, join_condition)

    total = await session.scalar(count_query.filter(*filters))

    if not total:
        return 0, []

    data = await session.scalars(
        query.filter(*filters)
        .order_by(
            *build_order_by(
                search.sort,
                order_mapping={
                    "name_original": Person.name_native,
                    "name_ua": Person.name_ua,
                    "name_en": Person.name_en,
                },
                tiebreaker=asc(Person.id),
                nullable=["name_ua", "name_en", "name_original"],
            )
        )
        .limit(limit)
        .offset(offset)
    )

    return total, data


def todo_person_filters(search: PersonTodoArgs) -> tuple[list, list]:
    and_filters, or_filters = [], []

    todo_field_columns = {
        "name_ua": Person.name_ua,
        "name_en": Person.name_en,
        "name_original": Person.name_native,
    }

    for entry in search.fields:
        negative = entry.startswith("-")
        column = todo_field_columns[entry[1:] if negative else entry]
        and_filters.append(
            and_(column != None, column != "")  # noqa: E711
            if negative
            else or_(column == None, column == "")  # noqa: E711
        )

    if not search.fields:
        or_filters = [
            or_(Person.name_ua == None, Person.name_ua == ""),        # noqa: E711
            or_(Person.name_en == None, Person.name_en == ""),        # noqa: E711
            or_(Person.name_native == None, Person.name_native == ""),  # noqa: E711
        ]

    return and_filters, or_filters
