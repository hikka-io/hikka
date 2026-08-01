from sqlalchemy.orm import with_loader_criteria
from app.service import get_my_score_subquery
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import with_expression
from sqlalchemy.orm import joinedload
from app import constants

from app.models import (
    CharacterCollectionContent,
    PersonCollectionContent,
    AnimeCollectionContent,
    MangaCollectionContent,
    NovelCollectionContent,
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

    if preview:
        options.append(
            with_loader_criteria(
                CollectionContent, CollectionContent.order <= 6
            )
        )

    return query.options(*options)
