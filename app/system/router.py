from fastapi import APIRouter, Request
from app.utils import get_settings
from .schemas import EventArgs
import aiohttp


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
