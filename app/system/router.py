from fastapi import APIRouter, Request
from .schemas import EventArgs
import aiohttp


router = APIRouter(include_in_schema=False)


@router.post("/event", status_code=202)
async def analytics_event(request: Request, args: EventArgs):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://analytics.hikka.io/api/event",
            data={
                "referrer": args.r,
                "domain": args.d,
                "name": args.n,
                "url": args.u,
            },
            headers={
                "User-Agent": request.headers.get("User-Agent", "unknown"),
                "X-Forwarded-For": request.headers.get(
                    "cf-connecting-ip",
                    request.headers.get("x-forwarded-for", "127.0.0.1"),
                ),
            },
        ):
            return {}
