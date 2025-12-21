from .dependencies import validate_artifact
from fastapi import APIRouter, Depends
from .schemas import ArtifactResponse
from app.models import Artifact


router = APIRouter(prefix="/artifacts", tags=["Artifacts"])


@router.get("/{username}/{name}", response_model=ArtifactResponse)
async def get_artifact(artifact: Artifact = Depends(validate_artifact)):
    return artifact


# @router.post("/{username}/{name}/privacy")
# async def update_artifact_privacy(artifact: Artifact):
#     pass
