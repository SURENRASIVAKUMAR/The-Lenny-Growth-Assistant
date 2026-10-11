from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.core.database import get_db
from backend.app.models.session import ChatSession, Message
from backend.app.schemas.session import SessionCreate, SessionUpdate, SessionResponse

router = APIRouter()

@router.get("", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    """List all sessions ordered by most recently updated."""
    sessions = (
        db.query(ChatSession)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    result = []
    for s in sessions:
        count = db.query(func.count(Message.id)).filter(Message.session_id == s.id).scalar() or 0
        result.append(
            SessionResponse(
                id=s.id,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=count,
            )
        )
    return result

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_in: SessionCreate, db: Session = Depends(get_db)):
    """Create a new chat session."""
    session = ChatSession(title=session_in.title or "New Conversation")
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0,
    )

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Retrieve details for a single session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    count = db.query(func.count(Message.id)).filter(Message.session_id == session.id).scalar() or 0
    return SessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=count,
    )

@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(session_id: str, session_in: SessionUpdate, db: Session = Depends(get_db)):
    """Rename a session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.title = session_in.title
    db.commit()
    db.refresh(session)
    count = db.query(func.count(Message.id)).filter(Message.session_id == session.id).scalar() or 0
    return SessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=count,
    )

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a session and all its associated messages and artifacts."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return None
