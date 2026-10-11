import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.core.config import settings
from backend.app.core.database import check_database_connection
from backend.app.api.endpoints import (
    health,
    sessions,
    messages,
    chat,
    knowledge,
    artifacts,
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("lenny_growth_assistant")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode...")
    db_status = check_database_connection()
    if db_status["status"] == "connected":
        logger.info(f"Database connection verified: {db_status['database_name']} on {db_status['host']}:{db_status['port']}")
    else:
        logger.warning(f"Database connection warning: {db_status.get('error')}")
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-stack AI assistant for Lenny's Podcast and Newsletter content with Ship 30 for 30 essay writing and sandboxed artifacts.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(health.router, prefix="/api", tags=["Health & Status"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(messages.router, prefix="/api/sessions", tags=["Messages"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat & Agent"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["Knowledge Base & RAG"])
app.include_router(artifacts.router, prefix="/api/artifacts", tags=["Artifacts"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please check application logs."},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
