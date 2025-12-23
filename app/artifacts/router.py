from sqlalchemy.ext.asyncio import AsyncSession
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

from .dependencies import (
    validate_artifact_owner,
    validate_artifact_info,
    validate_artifact,
)

router = APIRouter(prefix="/artifacts", tags=["Artifacts"])


@router.get("/{name}/privacy", response_model=ArtifactPrivacyResponse)
async def get_artifact_privacy(
    artifact: Artifact = Depends(validate_artifact_owner),
):
    return artifact


@router.get(
    "/{username}/{name}/privacy", response_model=ArtifactPrivacyResponse
)
async def get_user_artifact_privacy(
    artifact: Artifact = Depends(validate_artifact),
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
async def get_artifact(artifact: Artifact = Depends(validate_artifact_info)):
    return artifact
