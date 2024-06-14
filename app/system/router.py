from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_page, get_size
from .dependencies import validate_backup_token
from fastapi import APIRouter, Request, Depends
from .schemas import ImagesPaginationResponse
from app.database import get_session
from app.utils import get_settings
from .schemas import EventArgs
from . import service
import aiohttp

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(include_in_schema=False)


@router.post("/event", status_code=202)
async def analytics_event(request: Request, args: EventArgs):
    settings = get_settings()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.backend.plausible}/api/event",
                data={
                    "referrer": args.r,
                    "domain": args.d,
                    "name": args.n,
                    "url": args.u,
                },
                headers={
                    "User-Agent": request.headers.get("user-agent", "unknown"),
                    "Host": "analytics.hikka.io",
                    "X-Forwarded-Host": request.headers.get(
                        "x-forwarded-host", "hikka.io"
                    ),
                    "X-Forwarded-Proto": request.headers.get(
                        "x-forwarded-proto", "https"
                    ),
                    "X-Forwarded-For": request.headers.get(
                        "cf-connecting-ip",
                        request.headers.get("x-forwarded-for", "127.0.0.1"),
                    ),
                },
            ):
                return {}

    except aiohttp.ClientError:
        return {}


@router.get(
    "/backup/images",
    response_model=ImagesPaginationResponse,
    dependencies=[Depends(validate_backup_token)],
)
async def backup_images(
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_images_count(session)
    images = await service.get_images(session, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": images.all(),
    }
