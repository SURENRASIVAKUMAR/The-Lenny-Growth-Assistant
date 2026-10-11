import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.session import ChatSession, Message
from backend.app.schemas.message import MessageCreate, MessageResponse, Citation

router = APIRouter()

@router.get("/{session_id}/messages", response_model=List[MessageResponse])
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    """Retrieve all messages for a specific session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    
    result = []
    for m in messages:
        citations = []
        if m.citations:
            try:
                raw_citations = json.loads(m.citations)
                citations = [Citation(**c) for c in raw_citations]
            except Exception:
                citations = []
        result.append(
            MessageResponse(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                model_used=m.model_used,
                provider_used=m.provider_used,
                citations=citations,
                created_at=m.created_at,
            )
        )
    return result

@router.post("/{session_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_session_message(session_id: str, message_in: MessageCreate, db: Session = Depends(get_db)):
    """Add a message to a session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    citation_str = (
        json.dumps([c.model_dump() for c in message_in.citations])
        if message_in.citations
        else None
    )

    msg = Message(
        session_id=session_id,
        role=message_in.role,
        content=message_in.content,
        model_used=message_in.model_used,
        provider_used=message_in.provider_used,
        citations=citation_str,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return MessageResponse(
        id=msg.id,
        session_id=msg.session_id,
        role=msg.role,
        content=msg.content,
        model_used=msg.model_used,
        provider_used=msg.provider_used,
        citations=message_in.citations or [],
        created_at=msg.created_at,
    )
