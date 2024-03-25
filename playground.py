from app.sync.notifications import generate_notifications
from app.sync.aggregator.info import update_anime_info
from app.service import calculate_watch_duration
from app.sync.activity import generate_activity
from meilisearch_python_sdk import AsyncClient
from app.edit.utils import calculate_before
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from sqlalchemy import make_url, func
from app.utils import get_settings
from app.sync import update_search
from app.sync import sitemap
from app.sync import email
from app import constants
import asyncio
import math
import json

from app.admin.service import (
    create_hikka_update_notification,
    delete_hikka_update_notification,
)

from app.models import (
    CommentVoteLegacy,
    AnimeStaffRole,
    UserEditStats,
    CommentVote,
    AnimeStaff,
    AnimeWatch,
    Collection,
    Favourite,
    Comment,
    Anime,
    User,
    Edit,
    Log,
)


async def test_meiliserarch_ranking():
    settings = get_settings()

    # default = ["words", "typo", "proximity", "attribute", "sort", "exactness"]

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_ANIME)

        test = await index.get_ranking_rules()

        print(test)


async def query_activity():
    from datetime import datetime, timedelta
    from app.models import Activity

    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        threshold = datetime.utcnow() - timedelta(days=1)

        test = await session.scalar(
            select(Activity).filter(Activity.created > threshold)
        )

        print(test)

    await sessionmanager.close()


async def import_role_weights():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        with open("docs/roles.json", "r") as file:
            data = json.load(file)

            for entry in data["service_content_anime_staff_roles"]:
                role = await session.scalar(
                    select(AnimeStaffRole).filter(
                        AnimeStaffRole.slug == entry["slug"]
                    )
                )

                role.name_ua = entry["name_ua"]
                role.weight = entry["weight"]

                session.add(role)

            await session.commit()

    await sessionmanager.close()


async def recalculate_anime_staff_weights():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        limit = 10000
        total = await session.scalar(select(func.count(AnimeStaff.id)))
        pages = math.ceil(total / limit) + 1

        for page in range(1, pages):
            print(page)

            offset = (limit * (page)) - limit

            staff_roles = await session.scalars(
                select(AnimeStaff)
                .options(selectinload(AnimeStaff.roles))
                .order_by(desc(AnimeStaff.id))
                .limit(limit)
                .offset(offset)
            )

            for staff in staff_roles:
                staff.weight = sum([role.weight for role in staff.roles])
                session.add(staff)

            await session.commit()

    await sessionmanager.close()


async def test_sitemap():
    await sitemap.update_sitemap()


async def test_email_template():
    await email.send_emails()


async def test_check():
    settings = get_settings()
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
    url = make_url(settings.database.endpoint)
    print(url.password)


async def test():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)
    semaphore = asyncio.Semaphore(10)

    async with sessionmanager.session() as session:
        anime = await session.scalar(
            select(Anime).order_by(desc("score"), desc("scored_by")).limit(1)
        )

        await update_anime_info(semaphore, anime.content_id)

    await sessionmanager.close()


async def watch_stats():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        watch_entries = await session.scalars(
            select(AnimeWatch)
            .options(selectinload(AnimeWatch.anime))
            .filter(AnimeWatch.duration == 0)
            .limit(20000)
        )

        for watch in watch_entries:
            watch.duration = calculate_watch_duration(watch)
            session.add(watch)
            await session.commit()

    await sessionmanager.close()


async def fix_closed_edits():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        edits = await session.scalars(
            select(Edit).filter(Edit.before == None)  # noqa: E711
        )

        for edit in edits:
            edit.before = calculate_before(edit.content, edit.after)
            session.add(edit)

        await session.commit()

    await sessionmanager.close()


async def test_sync_stuff():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        await generate_activity(session)
        # await generate_notifications(session)
        # await generate_history(session)

    await sessionmanager.close()


async def test_system_notification():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        update_name = "hikka_profile_update"

        await create_hikka_update_notification(
            session,
            update_name,
            "Розказуємо про основні зміни за останні кілька тижнів",
            "Редизайн профілю, активність та сповіщення",
            "https://t.me/hikka_io/10",
        )

        # await delete_hikka_update_notification(session, update_name)

    await sessionmanager.close()


async def run_search():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await update_search()

    await sessionmanager.close()


async def run_migrate_logs():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        remove_logs = await session.scalars(
            select(Log).filter(
                Log.log_type == constants.LOG_FAVOURITE_ANIME_REMOVE
            )
        )

        for log in remove_logs:
            log.data = {"content_type": constants.CONTENT_ANIME}
            log.log_type = constants.LOG_FAVOURITE_REMOVE

            session.add(log)
            await session.commit()

            print(log)

        add_logs = await session.scalars(
            select(Log).filter(Log.log_type == constants.LOG_FAVOURITE_ANIME)
        )

        for log in add_logs:
            log.data = {"content_type": constants.CONTENT_ANIME}
            log.log_type = constants.LOG_FAVOURITE

            session.add(log)
            await session.commit()

            print(log)

    await sessionmanager.close()


async def calculate_stats():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        users = await session.scalars(select(User).filter(User.edits.any()))

        for user in users:
            accepted = await session.scalar(
                select(func.count(Edit.id)).filter(
                    Edit.author == user, Edit.status == constants.EDIT_ACCEPTED
                )
            )

            closed = await session.scalar(
                select(func.count(Edit.id)).filter(
                    Edit.author == user, Edit.status == constants.EDIT_CLOSED
                )
            )

            denied = await session.scalar(
                select(func.count(Edit.id)).filter(
                    Edit.author == user, Edit.status == constants.EDIT_DENIED
                )
            )

            if not (
                stats := await session.scalar(
                    select(UserEditStats).filter(UserEditStats.user == user)
                )
            ):
                stats = UserEditStats(
                    **{
                        "user": user,
                        "accepted": 0,
                        "closed": 0,
                        "denied": 0,
                    }
                )

            stats.accepted = accepted
            stats.closed = closed
            stats.denied = denied

            session.add(stats)
            await session.commit()

    await sessionmanager.close()


async def run_migrate_collections():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        collections = await session.scalars(select(Collection))

        for collection in collections:
            if collection.private:
                collection.visibility = constants.COLLECTION_UNLISTED

            session.add(collection)

        await session.commit()

    await sessionmanager.close()


async def run_migrate_votes():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        legacy_votes = await session.scalars(select(CommentVoteLegacy))

        for legacy_vote in legacy_votes:
            if await session.scalar(
                select(CommentVote).filter(
                    CommentVote.content_id == legacy_vote.comment_id,
                    CommentVote.user_id == legacy_vote.user_id,
                )
            ):
                print(
                    f"Found CommentVote record for {legacy_vote.comment_id}:{legacy_vote.user_id}"
                )

                continue

            vote = CommentVote(
                **{
                    "content_id": legacy_vote.comment_id,
                    "user_id": legacy_vote.user_id,
                    "created": legacy_vote.created,
                    "updated": legacy_vote.updated,
                    "score": legacy_vote.score,
                }
            )

            session.add(vote)

        await session.commit()

        comment_vote_logs = await session.scalars(
            select(Log).filter(Log.log_type == constants.LOG_COMMENT_VOTE)
        )

        for log in comment_vote_logs:
            log.log_type = constants.LOG_VOTE_SET
            log.data["content_type"] = constants.CONTENT_COMMENT

            session.add(log)

            print(f"Updated log {log.id}")

        await session.commit()

        comments = await session.scalars(select(Comment))

        for comment in comments:
            if vote_score := await session.scalar(
                select(func.sum(CommentVote.score)).filter(
                    CommentVote.content == comment
                )
            ):
                comment.vote_score = vote_score
                session.add(comment)

                print(
                    f"Updated vote score to {vote_score} for comment {comment.id}"
                )

        await session.commit()

    await sessionmanager.close()


async def spring_top():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        spring_result = await session.execute(
            select(Anime, func.count(Anime.id))
            .join(AnimeWatch, AnimeWatch.anime_id == Anime.id)
            .filter(AnimeWatch.status == constants.WATCH_PLANNED)
            .filter(Anime.year == 2024, Anime.season == constants.SEASON_SPRING)
            .group_by(Anime)
            .order_by(func.count(Anime.id).desc())
            .limit(10)
        )

        print("Spring 2024:")
        for anime, list_count in spring_result:
            print(
                list_count,
                f"https://hikka.io/anime/{anime.slug}",
            )

        winter_result = await session.execute(
            select(Anime, func.count(Anime.id))
            .join(AnimeWatch, AnimeWatch.anime_id == Anime.id)
            .filter(
                AnimeWatch.status.in_(
                    [
                        constants.WATCH_PLANNED,
                        constants.WATCH_WATCHING,
                        constants.WATCH_COMPLETED,
                    ]
                )
            )
            .filter(Anime.year == 2023, Anime.season == constants.SEASON_WINTER)
            .group_by(Anime)
            .order_by(func.count(Anime.id).desc())
            .limit(10)
        )

        print("Winter 2023:")
        for anime, list_count in winter_result:
            print(
                list_count,
                f"https://hikka.io/anime/{anime.slug}",
            )

    await sessionmanager.close()


def calculate_score(vote_score, favourite_count, comments_count):
    weight_vote_score = 1
    weight_favourite = 2
    weight_comments = 0.1

    return (
        (vote_score * weight_vote_score)
        + (favourite_count * weight_favourite)
        + (comments_count * weight_comments)
    )


async def collection_ranking():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        collections = await session.scalars(select(Collection))

        for collection in collections:
            favourite_count = await session.scalar(
                select(func.count(Favourite.id)).filter(
                    Favourite.content_type == constants.CONTENT_COMMENT,
                    Favourite.content_id == collection.id,
                )
            )

            comments_count = await session.scalar(
                select(func.count(Comment.id)).filter(
                    Comment.content_type == constants.CONTENT_COMMENT,
                    Comment.content_id == collection.id,
                    Comment.hidden == False,  # noqa: E712
                )
            )

            print(
                f"Vote: {collection.vote_score},",
                f"Favourite: {favourite_count},",
                f"Comments: {comments_count},",
                "Ranking: "
                + str(
                    calculate_score(
                        collection.vote_score,
                        favourite_count,
                        comments_count,
                    )
                )
                + ",",
                collection.title,
            )

    await sessionmanager.close()


if __name__ == "__main__":
    # asyncio.run(test_email_template())
    # asyncio.run(test_sitemap())
    # asyncio.run(test_check())
    # asyncio.run(import_role_weights())
    # asyncio.run(recalculate_anime_staff_weights())
    # asyncio.run(query_activity())
    # asyncio.run(test_sync_stuff())
    # asyncio.run(test_system_notification())
    # asyncio.run(run_search())
    # asyncio.run(watch_stats())
    # asyncio.run(fix_closed_edits())
    # asyncio.run(test())
    # asyncio.run(run_migrate_logs())
    # asyncio.run(calculate_stats())
    # asyncio.run(run_migrate_collections())
    # asyncio.run(run_migrate_votes())
    # asyncio.run(test_meiliserarch_ranking())
    # asyncio.run(spring_top())
    asyncio.run(collection_ranking())
    pass
