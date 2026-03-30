from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import Digest, User
from app.service import create_log
from app import constants
from . import service

from .schemas import (
    DigestPrivacyResponse,
    DigestResponse,
    PrivateArgs,
)

from .dependencies import (
    validate_digest_owner,
    validate_digest_info,
    validate_digest,
)

router = APIRouter(prefix="/digests", tags=["Digests"])


@router.get("/{name}/privacy", response_model=DigestPrivacyResponse)
async def get_digest_privacy(
    digest: Digest = Depends(validate_digest_owner),
):
    return digest


@router.get("/{username}/{name}/privacy", response_model=DigestPrivacyResponse)
async def get_user_digest_privacy(
    digest: Digest = Depends(validate_digest),
):
    return digest


@router.post("/{name}/privacy", response_model=DigestPrivacyResponse)
async def update_digest_privacy(
    args: PrivateArgs,
    digest: Digest = Depends(validate_digest_owner),
    request_user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
):
    await service.set_privacy(session, digest, args.private)
    await create_log(
        session,
        constants.LOG_ARTIFACT_PRIVACY,
        request_user,
        digest.id,
        {"private": args.private},
    )

    return digest


@router.get("/{username}/{name}", response_model=DigestResponse)
async def get_digest(digest: Digest = Depends(validate_digest_info)):
    return digest
