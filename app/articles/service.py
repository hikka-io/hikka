from sqlalchemy import select, desc, asc, case, and_, or_, func
from app.common.utils import find_document_images
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import with_expression
from app.common.service import get_images
from sqlalchemy.orm import joinedload
from app.utils import utcnow, slugify
from collections import defaultdict
from app import constants
from uuid import uuid4

from app.models import (
    UserArticleStats,
    ArticleComment,
    ArticleTag,
    Article,
    Anime,
    Manga,
    Novel,
    User,
)

from app.service import (
    get_followed_user_ids,
    get_my_score_subquery,
    get_user_by_username,
    get_content_by_slug,
    create_log,
)

from .schemas import (
    ArticlesListArgs,
    ArticleArgs,
)


async def get_or_create_tag(session: AsyncSession, name: str):
    if not (
        tag := await session.scalar(
            select(ArticleTag).filter(ArticleTag.name == name)
        )
    ):
        tag = ArticleTag(**{"content_count": 0, "name": name})
        session.add(tag)

    return tag


def build_articles_order_by(sort: list[str]):
    # TODO: Unified function for this stuff
    order_mapping = {
        "vote_score": Article.vote_score,
        "created": Article.created,
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


async def get_article_by_slug(
    session: AsyncSession, slug: str, request_user: User
):
    followed_user_ids = await get_followed_user_ids(session, request_user)

    article = await session.scalar(
        select(Article)
        .filter(Article.slug == slug)
        .filter(Article.deleted == False)  # noqa: E712
        .options(
            joinedload(Article.author).options(
                with_expression(
                    User.is_followed,
                    case((User.id.in_(followed_user_ids), True), else_=False),
                )
            )
        )
        .options(joinedload(Article.tags))
        .options(
            with_expression(
                Article.my_score,
                get_my_score_subquery(
                    Article, constants.CONTENT_ARTICLE, request_user
                ),
            )
        )
    )

    return await load_articles_content(session, article)


async def create_article(
    session: AsyncSession,
    args: ArticleArgs,
    user: User,
    content: Anime | Manga | Novel | None = None,
):
    now = utcnow()

    max_attempts = 5
    attempts = 0

    # Since we deal with user generated content
    # we have to make sure slug is unique
    while True:
        slug = slugify(args.title, uuid4())

        # If we exceed out attempts limit we just generate random slug
        if attempts > max_attempts:
            slug = str(uuid4())
            break

        if not await get_article_by_slug(session, slug, user):
            break

        attempts += 1

    tags = []

    for name in args.tags:
        tag = await get_or_create_tag(session, name)
        tag.content_count += 1
        tags.append(tag)

    article = Article(
        **{
            "category": args.category,
            "document": args.document,
            "trusted": args.trusted,
            "draft": args.draft,
            "title": args.title,
            "deleted": False,
            "vote_score": 0,
            "author": user,
            "created": now,
            "updated": now,
            "tags": tags,
            "slug": slug,
        }
    )

    if content:
        article.content_type = args.content.content_type
        article.content_id = content.id

    session.add(article)

    await session.commit()

    image_nodes = find_document_images(args.document)
    urls = list(set([entry["url"] for entry in image_nodes]))
    images = await get_images(session, urls)

    for image in images:
        image.attachment_content_type = constants.CONTENT_ARTICLE
        image.attachment_content_id = article.id

    await create_log(
        session,
        constants.LOG_ARTICLE_CREATE,
        user,
        article.id,
        {
            "content_type": article.content_type,
            "content_id": article.reference,
            "document": article.document,
            "category": article.category,
            "trusted": article.trusted,
            "draft": article.draft,
            "title": article.title,
            "slug": article.slug,
            "tags": args.tags,
        },
    )

    # Simple hack to init my_score with 0
    # TODO: fixme!!!
    article.author.is_followed = False
    article.my_score = 0

    await load_articles_content(session, article)

    return article


async def update_article(
    session: AsyncSession,
    article: Article,
    args: ArticleArgs,
    user: User,
    content: Anime | Manga | Novel | None = None,
):
    before = {}
    after = {}

    old_document = article.document

    # If article draft changed to false we shall update creation time
    update_created = article.draft is True and args.draft is False

    for key in ["category", "draft", "title", "document", "trusted"]:
        old_value = getattr(article, key)
        new_value = getattr(args, key)

        if old_value != new_value:
            before[key] = old_value
            setattr(article, key, new_value)
            after[key] = new_value

    # Here we mark old images as delted and new as used
    old_image_nodes = find_document_images(old_document)
    old_urls = set([entry["url"] for entry in old_image_nodes])

    new_image_nodes = find_document_images(args.document)
    new_urls = set([entry["url"] for entry in new_image_nodes])

    old_images = await get_images(session, list(old_urls - new_urls))
    new_images = await get_images(session, list(new_urls - old_urls))

    for image in old_images:
        image.attachment_content_type = None
        image.attachment_content_id = None
        image.deletion_request = True

    for image in new_images:
        image.attachment_content_type = constants.CONTENT_ARTICLE
        image.attachment_content_id = article.id

    # Content being removed from the article
    if content is None and article.content_id is not None:
        before["content_type"] = article.content_type
        before["content_id"] = str(article.content_id)

        article.content_type = None
        article.content_id = None

        after["content_type"] = None
        after["content_id"] = None

    if content:
        # New content being added to article
        if article.content_id is None:
            before["content_type"] = None
            before["content_id"] = None

        # Convent being replaced in article
        else:
            before["content_type"] = article.content_type
            before["content_id"] = str(article.content_id)

        article.content_type = args.content.content_type
        article.content_id = content.id

        after["content_type"] = article.content_type
        after["content_id"] = str(article.content_id)

    # Update tags
    # TODO: we probably should do that in sync to prevent inconsistencies
    old_tags = article.tags
    new_tags = []

    for name in args.tags:
        tag = await get_or_create_tag(session, name)
        new_tags.append(tag)

    old_tag_names = set([tag.name for tag in old_tags])
    new_tag_names = set([tag.name for tag in new_tags])

    if old_tag_names != new_tag_names:
        before["tags"] = list(old_tag_names)
        after["tags"] = list(new_tag_names)
        article.tags = new_tags

        for tag in old_tags:
            tag.content_count -= 1

        for tag in new_tags:
            tag.content_count += 1

    now = utcnow()
    article.updated = now

    if update_created:
        article.created = now

    session.add(article)
    await session.commit()

    if before != {} and after != {}:
        await create_log(
            session,
            constants.LOG_ARTICLE_UPDATE,
            user,
            article.id,
            {
                "before": before,
                "after": after,
            },
        )

    return article


async def delete_article(session: AsyncSession, article: Article, user: User):
    # Here we mark old images as delted and new as used
    image_nodes = find_document_images(article.document)
    image_urls = set([entry["url"] for entry in image_nodes])

    images = await get_images(session, image_urls)

    for image in images:
        image.attachment_content_type = None
        image.attachment_content_id = None
        image.deletion_request = True

    for tag in article.tags:
        tag.content_count -= 1

    article.deleted = True
    session.add(article)

    # Mark comments for deleted article as private
    await session.execute(
        update(ArticleComment)
        .filter(ArticleComment.content == article)
        .values(private=True)
    )

    await session.commit()

    await create_log(
        session,
        constants.LOG_ARTICLE_DELETE,
        user,
        article.id,
    )

    return True


async def articles_list_filter(
    query: Select,
    request_user: User | None,
    args: ArticlesListArgs,
    session: AsyncSession,
):
    # We don't want to display system articles in global list
    query = query.filter(Article.category != constants.ARTICLE_SYSTEM)

    if len(args.categories) > 0:
        query = query.filter(Article.category.in_(args.categories))

    if args.show_trusted is True and args.min_vote_score is not None:
        query = query.filter(
            or_(
                Article.vote_score >= args.min_vote_score,
                Article.trusted == True,  # noqa: E712
            )
        )

    if args.show_trusted is False and args.min_vote_score is not None:
        query = query.filter(Article.vote_score >= args.min_vote_score)

    if len(args.tags) > 0:
        query = query.filter(
            and_(
                *[
                    Article.tags.any(ArticleTag.name == name)
                    for name in args.tags
                ]
            )
        )

    if args.content_type:
        query = query.filter(Article.content_type == args.content_type)

    if args.content_slug:
        content = await get_content_by_slug(
            session, args.content_type, args.content_slug
        )

        query = query.filter(Article.content_id == content.id)

    if args.author:
        author = await get_user_by_username(session, args.author)
        query = query.filter(Article.author == author)

    if args.draft:
        query = query.filter(
            Article.author == request_user,
            Article.draft == True,  # noqa: E712
        )

    else:
        query = query.filter(Article.draft == False)  # noqa: E712

    query = query.filter(
        Article.deleted == False,  # noqa: E712
    )

    return query


async def get_articles_count(
    session: AsyncSession,
    request_user: User | None,
    args: ArticlesListArgs,
) -> int:
    query = await articles_list_filter(
        select(func.count(Article.id)),
        request_user,
        args,
        session,
    )

    return await session.scalar(query)


async def get_articles(
    session: AsyncSession,
    request_user: User | None,
    args: ArticlesListArgs,
    limit: int,
    offset: int,
) -> list[Article]:
    followed_user_ids = await get_followed_user_ids(session, request_user)

    query = await articles_list_filter(
        select(Article)
        .options(
            joinedload(Article.author).options(
                with_expression(
                    User.is_followed,
                    case((User.id.in_(followed_user_ids), True), else_=False),
                )
            )
        )
        .options(
            with_expression(
                Article.my_score,
                get_my_score_subquery(
                    Article, constants.CONTENT_ARTICLE, request_user
                ),
            )
        ),
        request_user,
        args,
        session,
    )

    return await session.scalars(
        query.order_by(*build_articles_order_by(args.sort))
        .limit(limit)
        .offset(offset)
    )


async def load_articles_content(
    session: AsyncSession,
    article_or_articles: Article | list[Article],
):
    if isinstance(article_or_articles, Article):
        articles = [article_or_articles]
        single_input = True
    else:
        articles = article_or_articles
        single_input = False

    # No articles so why bother
    if not articles:
        return article_or_articles

    references = defaultdict(set)

    for article in articles:
        if article.content_type and article.content_id:
            references[article.content_type].add(article.content_id)

    anime_dict, manga_dict, novel_dict = {}, {}, {}

    if constants.CONTENT_ANIME in references:
        anime = await session.scalars(
            select(Anime).filter(
                Anime.id.in_(list(references[constants.CONTENT_ANIME]))
            )
        )

        anime_dict = {entry.id: entry for entry in anime.all()}

    if constants.CONTENT_MANGA in references:
        manga = await session.scalars(
            select(Manga).filter(
                Manga.id.in_(list(references[constants.CONTENT_MANGA]))
            )
        )

        manga_dict = {entry.id: entry for entry in manga.all()}

    if constants.CONTENT_NOVEL in references:
        novel = await session.scalars(
            select(Novel).filter(
                Novel.id.in_(list(references[constants.CONTENT_NOVEL]))
            )
        )

        novel_dict = {entry.id: entry for entry in novel.all()}

    for article in articles:
        match article.content_type:
            case constants.CONTENT_ANIME:
                article.content = anime_dict.get(article.content_id)

            case constants.CONTENT_MANGA:
                article.content = manga_dict.get(article.content_id)

            case constants.CONTENT_NOVEL:
                article.content = novel_dict.get(article.content_id)

            case _:
                article.content = None

    return articles[0] if single_input else articles


async def get_article_tags(session: AsyncSession):
    return await session.scalars(
        select(ArticleTag)
        .filter(ArticleTag.content_count > 0)
        .order_by(ArticleTag.content_count.desc(), ArticleTag.name.asc())
        .limit(10)
    )


async def get_article_authors(session: AsyncSession, request_user: User):
    followed_user_ids = await get_followed_user_ids(session, request_user)

    return await session.scalars(
        select(UserArticleStats)
        .options(
            joinedload(UserArticleStats.user).options(
                with_expression(
                    User.is_followed,
                    case((User.id.in_(followed_user_ids), True), else_=False),
                )
            )
        )
        .order_by(UserArticleStats.author_score.desc())
    )
