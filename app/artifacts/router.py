from .dependencies import validate_artifact_owner
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import validate_artifact
from app.dependencies import auth_required
from fastapi import APIRouter, Depends
from app.models import Artifact, User
from app.database import get_session
from app.service import create_log
from app import constants
from . import service

from .schemas import (
    ArtifactPrivacyResponse,
    ArtifactResponse,
    PrivateArgs,
)


router = APIRouter(prefix="/artifacts", tags=["Artifacts"])


@router.get("/{name}/privacy", response_model=ArtifactPrivacyResponse)
async def get_artifact_privacy(
    args: PrivateArgs,
    artifact: Artifact = Depends(validate_artifact_owner),
    session: AsyncSession = Depends(get_session),
):
    return artifact


@router.post("/{name}/privacy", response_model=ArtifactPrivacyResponse)
async def update_artifact_privacy(
    args: PrivateArgs,
    artifact: Artifact = Depends(validate_artifact_owner),
    request_user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
):
    await service.set_privacy(session, artifact, args.private)
    await create_log(
        session,
        constants.LOG_ARTIFACT_PRIVACY,
        request_user,
        artifact.id,
        {"private": args.private},
    )

    return artifact


@router.get("/{username}/{name}", response_model=ArtifactResponse)
async def get_artifact(artifact: Artifact = Depends(validate_artifact)):
    return artifact
