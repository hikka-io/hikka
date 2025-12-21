from .schemas import ArtifactResponse, PrivateArgs
from .dependencies import validate_artifact_owner
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import validate_artifact
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import Artifact
from . import service


router = APIRouter(prefix="/artifacts", tags=["Artifacts"])


@router.get("/{username}/{name}", response_model=ArtifactResponse)
async def get_artifact(artifact: Artifact = Depends(validate_artifact)):
    return artifact


@router.post("/{name}/privacy")
async def update_artifact_privacy(
    args: PrivateArgs,
    artifact: Artifact = Depends(validate_artifact_owner),
    session: AsyncSession = Depends(get_session),
):
    await service.set_privacy(session, artifact, args.private)
    return {"success": True}
