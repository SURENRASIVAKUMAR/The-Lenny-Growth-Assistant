import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

database_url = settings.get_database_url()

# Connection pool setup
# pool_pre_ping verifies connections are alive before handing them out
engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 3600,
}

if "sqlite" in database_url:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(database_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_database_connection() -> dict:
    """Verifies database connectivity and returns connection metadata."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            return {
                "status": "connected" if result == 1 else "unexpected_result",
                "database_name": settings.DB_NAME,
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
                "driver": settings.DB_DRIVER,
                "error": None
            }
    except Exception as exc:
        logger.error(f"Database connection error: {exc}")
        return {
            "status": "disconnected",
            "database_name": settings.DB_NAME,
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "driver": settings.DB_DRIVER,
            "error": str(exc)
        }
