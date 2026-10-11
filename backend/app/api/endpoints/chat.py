import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.message import ChatRequest, ChatResponse
from backend.app.services.agent.orchestrator import execute_agent_chat

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint:
    Processes user query through RAG pipeline, AI provider, and artifact extractor.
    Supports standard question answering and dedicated Ship 30 for 30 essay writing.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty."
        )

    try:
        response = await execute_agent_chat(request, db)
        return response
    except ValueError as ve:
        logger.warning(f"Validation or configuration error in chat: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Internal error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating the response: {str(e)}"
        )
