from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app import constants
from app.database import get_session
from app.dependencies import auth_required, get_page, get_size
from app.manga.schemas import MangaPaginationResponse
from app.models import Anime, Character, Edit, Manga, Novel, Person, User
from app.novel.schemas import NovelPaginationResponse
from app.schemas import AnimePaginationResponse
from app.utils import paginated_response, pagination

from . import service

from .dependencies import (
    validate_content, 
    validate_edit_accept,
    validate_edit_close, 
    validate_edit_create,
    validate_edit_create_rate_limit, 
    validate_edit_id,
    validate_edit_id_pending, 
    validate_edit_search_args,
    validate_edit_update, 
    validate_edit_update_args,
    validate_edit_update_rate_limit
)

from .schemas import (
    ContentToDoEnum, 
    EditArgs, 
    EditContentToDoEnum,
    EditContentTypeEnum, 
    EditListResponse, 
    EditResponse,
    EditSearchArgs,
    TodoListResponse,
    AnimeTodoArgs,
    TodoAnimeResponse,
    MangaTodoArgs,
    TodoMangaResponse,
    NovelTodoArgs,
    TodoNovelResponse,
    CharacterTodoArgs,
    TodoCharacterResponse,
    PersonTodoArgs,
    TodoPersonResponse
)

router = APIRouter(prefix="/edit", tags=["Edit"])


@router.post("/list", response_model=EditListResponse)
async def get_edits(
    args: EditSearchArgs = Depends(validate_edit_search_args),
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.count_edits(session, args)
    edits = await service.get_edits(session, args, limit, offset)

    return paginated_response(edits.all(), total, page, limit)


@router.get("/{edit_id}", response_model=EditResponse)
async def get_edit(edit: Edit = Depends(validate_edit_id)):
    return edit


@router.put("/{content_type}/{slug}", response_model=EditResponse)
async def create_edit(
    content_type: EditContentTypeEnum,
    session: AsyncSession = Depends(get_session),
    content: Person | Anime | Manga | Novel | Character = Depends(
        validate_content
    ),
    args: EditArgs = Depends(validate_edit_create),
    author: User = Depends(validate_edit_create_rate_limit),
):
    return await service.create_pending_edit(
        session, content_type, content, args, author
    )


@router.post("/{edit_id}/update", response_model=EditResponse)
async def update_edit(
    session: AsyncSession = Depends(get_session),
    args: EditArgs = Depends(validate_edit_update_args),
    edit: Edit = Depends(validate_edit_update),
    user: User = Depends(validate_edit_update_rate_limit),
):
    return await service.update_pending_edit(session, edit, user, args)


@router.post("/{edit_id}/close", response_model=EditResponse)
async def close_edit(
    session: AsyncSession = Depends(get_session),
    edit: Edit = Depends(validate_edit_close),
):
    return await service.close_pending_edit(session, edit)


@router.post("/{edit_id}/accept", response_model=EditResponse)
async def accept_edit(
    session: AsyncSession = Depends(get_session),
    edit: Edit = Depends(validate_edit_accept),
    moderator: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_EDIT_ACCEPT],
            scope=[constants.SCOPE_ACCEPT_EDIT],
        )
    ),
):
    return await service.accept_pending_edit(session, edit, moderator)


@router.post("/{edit_id}/deny", response_model=EditResponse)
async def deny_edit(
    session: AsyncSession = Depends(get_session),
    edit: Edit = Depends(validate_edit_id_pending),
    moderator: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_EDIT_ACCEPT],
            scope=[constants.SCOPE_DENY_EDIT],
        )
    ),
):
    return await service.deny_pending_edit(session, edit, moderator)


@router.get(
    "/todo/{content_type}/{todo_type}",
    response_model=AnimePaginationResponse
    | MangaPaginationResponse
    | NovelPaginationResponse,
    # TODO: remove this deprecated route
    # Replaced by the five (5) dedicated /todo endpoints below. While anime,
    # manga and novels share a similar interface, characters and people
    # diverge enough that a single generic endpoint cannot cover them all
    deprecated=True,
)
async def get_content_edit_todo(
    content_type: EditContentToDoEnum,
    todo_type: ContentToDoEnum,
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(
        auth_required(
            optional=True,
            scope=[
                constants.SCOPE_READ_READLIST,
                constants.SCOPE_READ_WATCHLIST,
            ],
        )
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.content_todo_total(session, content_type, todo_type)
    content = await service.content_todo(
        session, content_type, todo_type, request_user, limit, offset
    )

    return paginated_response(content.unique().all(), total, page, limit)


@router.get(
    "/todo/anime",
    response_model=TodoListResponse[TodoAnimeResponse],
    summary="Return list of anime with issues",
)
async def get_todo_anime_list(
    session: AsyncSession = Depends(get_session),
    search: AnimeTodoArgs = Depends(),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)

    total, data = await service.get_todo_anime_list(
        session, limit, offset, search
    )

    dto = [TodoAnimeResponse.from_(anime) for anime in data]

    return paginated_response(dto, total, page, limit)


@router.get(
    "/todo/manga",
    response_model=TodoListResponse[TodoMangaResponse],
    summary="Return list of manga with issues",
)
async def get_todo_manga_list(
    session: AsyncSession = Depends(get_session),
    search: MangaTodoArgs = Depends(),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)

    total, data = await service.get_todo_manga_list(
        session, limit, offset, search
    )

    dto = [TodoMangaResponse.from_(manga) for manga in data]

    return paginated_response(dto, total, page, limit)


@router.get(
    "/todo/novel",
    response_model=TodoListResponse[TodoNovelResponse],
    summary="Return list of novel with issues",
)
async def get_todo_novel_list(
    session: AsyncSession = Depends(get_session),
    search: NovelTodoArgs = Depends(),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)

    total, data = await service.get_todo_novel_list(
        session, limit, offset, search
    )

    dto = [TodoNovelResponse.from_(novel) for novel in data]

    return paginated_response(dto, total, page, limit)


@router.get(
    "/todo/characters",
    response_model=TodoListResponse[TodoCharacterResponse],
    summary="Return list of characters with issues",
)
async def get_todo_character_list(
    session: AsyncSession = Depends(get_session),
    search: CharacterTodoArgs = Depends(),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)

    total, data = await service.get_todo_character_list(
        session, limit, offset, search
    )

    dto = [TodoCharacterResponse.from_(character) for character in data]

    return paginated_response(dto, total, page, limit)


@router.get(
    "/todo/people",
    response_model=TodoListResponse[TodoPersonResponse],
    summary="Return list of people with issues",
)
async def get_todo_person_list(
    session: AsyncSession = Depends(get_session),
    search: PersonTodoArgs = Depends(),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)

    total, data = await service.get_todo_person_list(
        session, limit, offset, search
    )

    dto = [TodoPersonResponse.from_(person) for person in data]

    return paginated_response(dto, total, page, limit)
