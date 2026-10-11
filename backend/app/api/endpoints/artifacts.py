from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.artifact import Artifact
from backend.app.schemas.artifact import ArtifactCreate, ArtifactUpdate, ArtifactResponse

router = APIRouter()

@router.get("", response_model=List[ArtifactResponse])
def list_artifacts(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    db: Session = Depends(get_db)
):
    """List artifacts, optionally filtered by session_id."""
    query = db.query(Artifact)
    if session_id:
        query = query.filter(Artifact.session_id == session_id)
    artifacts = query.order_by(Artifact.updated_at.desc()).all()
    return artifacts

@router.get("/{artifact_id}", response_model=ArtifactResponse)
def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    """Retrieve an artifact by ID."""
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact

@router.post("", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
def create_artifact(artifact_in: ArtifactCreate, db: Session = Depends(get_db)):
    """Create a new artifact."""
    artifact = Artifact(
        session_id=artifact_in.session_id,
        title=artifact_in.title,
        artifact_type=artifact_in.artifact_type,
        content=artifact_in.content,
        metadata_json=artifact_in.metadata_json,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact

@router.patch("/{artifact_id}", response_model=ArtifactResponse)
def update_artifact(artifact_id: str, artifact_in: ArtifactUpdate, db: Session = Depends(get_db)):
    """Update an existing artifact."""
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    if artifact_in.title is not None:
        artifact.title = artifact_in.title
    if artifact_in.content is not None:
        artifact.content = artifact_in.content
    if artifact_in.artifact_type is not None:
        artifact.artifact_type = artifact_in.artifact_type
    if artifact_in.metadata_json is not None:
        artifact.metadata_json = artifact_in.metadata_json

    db.commit()
    db.refresh(artifact)
    return artifact

@router.delete("/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artifact(artifact_id: str, db: Session = Depends(get_db)):
    """Delete an artifact."""
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    db.delete(artifact)
    db.commit()
    return None
