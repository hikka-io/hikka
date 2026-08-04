from pydantic import ValidationError
from app import constants

from app.models import (
    Anime,
    Manga,
    Novel,
    Character,
    Person,
    Edit,
)

from .schemas import (
    CharacterEditArgs,
    EditContentTypeEnum,
    PersonEditArgs,
    AnimeEditArgs,
    MangaEditArgs,
    NovelEditArgs,
    EditArgs,
    AnimeTodoArgs,
    MangaTodoArgs,
    NovelTodoArgs,
    CharacterTodoArgs,
    PersonTodoArgs,
)


def check_edit_schema(
    content_type: EditContentTypeEnum,
    args: EditArgs,
):
    # Make sure we know how to validate proposed content changes
    schemas = {
        constants.CONTENT_CHARACTER: CharacterEditArgs,
        constants.CONTENT_PERSON: PersonEditArgs,
        constants.CONTENT_ANIME: AnimeEditArgs,
        constants.CONTENT_MANGA: MangaEditArgs,
        constants.CONTENT_NOVEL: NovelEditArgs,
    }

    if not (schema := schemas.get(content_type)):
        return False

    # Validate after field with provided schema
    # This check heavily depends on Pydantic's extra="forbid" option
    try:
        schema(**args.after)
    except ValidationError:
        return False

    return True


def check_invalid_fields(edit: Edit):
    """Check if content has unknown fields"""

    for key, _ in edit.after.items():
        if not hasattr(edit.content, key):
            return True

    return False


def check_after(after, content):
    """Check if Edit has differences from content"""

    pop_list = []

    for key, value in after.items():
        if getattr(content, key) == value:
            pop_list.append(key)

    for pop_key in pop_list:
        after.pop(pop_key)

    return after


def calculate_before(content, after):
    before = {}

    for key, _ in after.items():
        before[key] = getattr(content, key)

    return before


def todo_anime_filters(search: AnimeTodoArgs) -> tuple[list, list]:
    and_filters = [Anime.deleted == False]
    or_filters = []

    if search.media_type:
        and_filters.append(Anime.media_type == search.media_type)
    else:
        # Exclude music by default for backward compatibility with the
        # previous API endpoint @router.get("/todo/{content_type}/{todo_type}")
        # NOTE: Probably redundant, need check with the moderation team
        and_filters.append(~Anime.media_type.in_([constants.MEDIA_TYPE_MUSIC]))

    if search.mal_id is not None:
        and_filters.append(Anime.mal_id == search.mal_id)

    if search.title_ua:
        and_filters.append(Anime.title_ua == None)                  # noqa: E711

    if search.title_en:
        and_filters.append(Anime.title_en == None)                  # noqa: E711

    if search.title_original:
        # TODO: Field `Anime.title_ja` is preventing me from collapsing three 
        # functions todo_anime_filters, todo_manga_filters, todo_novel_filters 
        # into one generic function with following signature
        #  
        # def todo_content_filters(
        #       search: AnimeTodoArgs | MangaTodoArgs | NovelTodoArgs, 
        #       model:  Anime | Manga | Novel
        # ) -> tuple[list, list]: . . .
        and_filters.append(Anime.title_ja == None)                  # noqa: E711

    if search.synopsis_ua:
        and_filters.append(Anime.synopsis_ua == None)               # noqa: E711

    if search.synopsis_en:
        and_filters.append(Anime.synopsis_en == None)               # noqa: E711

    if not any(
        [
            search.title_ua,
            search.title_en,
            search.title_original,
            search.synopsis_ua,
            search.synopsis_en,
        ]
    ):
        or_filters = [
            Anime.title_ua == None,                                 # noqa: E711
            Anime.title_en == None,                                 # noqa: E711
            Anime.title_ja == None,                                 # noqa: E711
            Anime.synopsis_ua == None,                              # noqa: E711
            Anime.synopsis_en == None,                              # noqa: E711
        ]

    return and_filters, or_filters


def todo_manga_filters(search: MangaTodoArgs) -> tuple[list, list]:
    and_filters = [Manga.deleted == False]
    or_filters = []

    if search.media_type:
        and_filters.append(Manga.media_type == search.media_type)

    if search.mal_id is not None:
        and_filters.append(Manga.mal_id == search.mal_id)

    if search.title_ua:
        and_filters.append(Manga.title_ua == None)                  # noqa: E711

    if search.title_en:
        and_filters.append(Manga.title_en == None)                  # noqa: E711

    if search.title_original:
        and_filters.append(Manga.title_original == None)            # noqa: E711

    if search.synopsis_ua:
        and_filters.append(Manga.synopsis_ua == None)               # noqa: E711

    if search.synopsis_en:
        and_filters.append(Manga.synopsis_en == None)               # noqa: E711

    if not any([
            search.title_ua,
            search.title_en,
            search.title_original,
            search.synopsis_ua,
            search.synopsis_en,
    ]):
        or_filters = [
            Manga.title_ua == None,                                 # noqa: E711
            Manga.title_en == None,                                 # noqa: E711
            Manga.title_original == None,                           # noqa: E711
            Manga.synopsis_ua == None,                              # noqa: E711
            Manga.synopsis_en == None,                              # noqa: E711
        ]

    return and_filters, or_filters


def todo_novel_filters(search: NovelTodoArgs) -> tuple[list, list]:
    and_filters = [Novel.deleted == False]
    or_filters = []

    if search.media_type:
        and_filters.append(Novel.media_type == search.media_type)

    if search.mal_id is not None:
        and_filters.append(Novel.mal_id == search.mal_id)

    if search.title_ua:
        and_filters.append(Novel.title_ua == None)                  # noqa: E711

    if search.title_en:
        and_filters.append(Novel.title_en == None)                  # noqa: E711

    if search.title_original:
        and_filters.append(Novel.title_original == None)            # noqa: E711

    if search.synopsis_ua:
        and_filters.append(Novel.synopsis_ua == None)               # noqa: E711

    if search.synopsis_en:
        and_filters.append(Novel.synopsis_en == None)               # noqa: E711

    if not any([
        search.title_ua,
        search.title_en,
        search.title_original,
        search.synopsis_ua,
        search.synopsis_en,
    ]):
        or_filters = [
            Novel.title_ua == None,                                 # noqa: E711
            Novel.title_en == None,                                 # noqa: E711
            Novel.title_original == None,                           # noqa: E711
            Novel.synopsis_ua == None,                              # noqa: E711
            Novel.synopsis_en == None,                              # noqa: E711
        ]

    return and_filters, or_filters


def todo_character_filters(search: CharacterTodoArgs) -> tuple[list, list]:
    and_filters, or_filters = [], []

    if search.name_ua:
        and_filters.append(Character.name_ua == None)               # noqa: E711

    if search.name_en:
        and_filters.append(Character.name_en == None)               # noqa: E711

    if search.name_original:
        and_filters.append(Character.name_ja == None)               # noqa: E711

    if search.description_ua:
        and_filters.append(Character.description_ua == None)        # noqa: E711

    if not any([
        search.name_ua,
        search.name_en,
        search.name_original,
        search.description_ua,
    ]):
        or_filters = [
            Character.name_ua == None,                              # noqa: E711
            Character.name_en == None,                              # noqa: E711
            Character.name_ja == None,                              # noqa: E711
            Character.description_ua == None,                       # noqa: E711
        ]

    return and_filters, or_filters


def todo_person_filters(search: PersonTodoArgs) -> tuple[list, list]:
    and_filters, or_filters = [], []

    if search.name_ua:
        and_filters.append(Person.name_ua == None)                  # noqa: E711

    if search.name_en:
        and_filters.append(Person.name_en == None)                  # noqa: E711

    if search.name_original:
        and_filters.append(Person.name_native == None)              # noqa: E711

    if not any([
        search.name_ua,
        search.name_en,
        search.name_original,
    ]):
        or_filters = [
            Person.name_ua == None,                                 # noqa: E711
            Person.name_en == None,                                 # noqa: E711
            Person.name_native == None,                             # noqa: E711
        ]

    return and_filters, or_filters
