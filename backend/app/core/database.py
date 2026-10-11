import logging
import socket
import time
from typing import Tuple, Dict, Any, Optional
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

# Connection pool configurations
_PG_URL = settings.get_database_url()
_MYSQL_URL = settings.MYSQL_DATABASE_URL or "mysql+pymysql://root:@localhost:3306/lenny_growth_assistant"
_SQLITE_URL = "sqlite:///./lenny_growth_assistant_fallback.db"

_pg_engine: Optional[Engine] = None
_mysql_engine: Optional[Engine] = None
_sqlite_engine: Optional[Engine] = None

# Cached engine state to minimize port checks
_last_check_time: float = 0.0
_cached_active_type: str = "unknown"
_cached_engine: Optional[Engine] = None
_CACHE_TTL_SECONDS = 15.0

def _is_port_open(host: str, port: int, timeout_sec: float = 0.06) -> bool:
    """Fast non-blocking port check."""
    try:
        # Resolve 'localhost' to 127.0.0.1 for fast TCP connection
        target_host = "127.0.0.1" if host in ("localhost", "::1") else host
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout_sec)
            s.connect((target_host, port))
            return True
    except Exception:
        return False

def get_pg_engine() -> Engine:
    global _pg_engine
    if _pg_engine is None:
        _pg_engine = create_engine(
            _PG_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
            max_overflow=20,
            connect_args={"connect_timeout": 2} if "psycopg" in _PG_URL else {}
        )
    return _pg_engine

def get_mysql_engine() -> Engine:
    global _mysql_engine
    if _mysql_engine is None:
        _mysql_engine = create_engine(
            _MYSQL_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
            max_overflow=20
        )
    return _mysql_engine

def get_sqlite_engine() -> Engine:
    global _sqlite_engine
    if _sqlite_engine is None:
        _sqlite_engine = create_engine(
            _SQLITE_URL,
            connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(bind=_sqlite_engine)
    return _sqlite_engine

def resolve_active_engine(force_refresh: bool = False) -> Tuple[Engine, str]:
    """
    Resolves the active database engine with automatic fallback:
    1. Primary PostgreSQL (if service is running on host:port)
    2. Fallback MySQL (if PostgreSQL is down and MySQL is running)
    3. Fallback SQLite (if neither is reachable)
    """
    global _last_check_time, _cached_active_type, _cached_engine
    now = time.time()
    
    if not force_refresh and _cached_engine is not None and (now - _last_check_time < _CACHE_TTL_SECONDS):
        return _cached_engine, _cached_active_type

    # 1. Check primary PostgreSQL
    pg_host = settings.DB_HOST or "localhost"
    pg_port = settings.DB_PORT or 5432
    if _is_port_open(pg_host, pg_port):
        try:
            eng = get_pg_engine()
            with eng.connect() as conn:
                conn.execute(text("SELECT 1"))
            _cached_active_type = "postgresql"
            _cached_engine = eng
            _last_check_time = now
            return eng, "postgresql"
        except Exception as e:
            logger.debug(f"PostgreSQL port open but handshake failed: {e}")

    # 2. Check fallback MySQL
    if _is_port_open("127.0.0.1", 3306):
        try:
            eng = get_mysql_engine()
            with eng.connect() as conn:
                conn.execute(text("SELECT 1"))
            _cached_active_type = "mysql"
            _cached_engine = eng
            _last_check_time = now
            return eng, "mysql"
        except Exception as e:
            logger.warning(f"MySQL fallback connection failed: {e}")

    # 3. Fallback SQLite
    eng = get_sqlite_engine()
    _cached_active_type = "sqlite"
    _cached_engine = eng
    _last_check_time = now
    return eng, "sqlite"

class _DynamicSessionMaker:
    """Creates sessions dynamically bound to the current active database engine."""
    def __call__(self, **kwargs) -> Session:
        eng, _ = resolve_active_engine()
        maker = sessionmaker(autocommit=False, autoflush=False, bind=eng)
        return maker(**kwargs)

SessionLocal = _DynamicSessionMaker()

def get_db():
    """FastAPI dependency for yielding database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class _EngineProxy:
    """Proxy object delegating calls to the currently active engine."""
    def __getattr__(self, name: str) -> Any:
        eng, _ = resolve_active_engine()
        return getattr(eng, name)
    def connect(self, *args, **kwargs):
        eng, _ = resolve_active_engine()
        return eng.connect(*args, **kwargs)
    def begin(self, *args, **kwargs):
        eng, _ = resolve_active_engine()
        return eng.begin(*args, **kwargs)
    def execution_options(self, *args, **kwargs):
        eng, _ = resolve_active_engine()
        return eng.execution_options(*args, **kwargs)

engine = _EngineProxy()

def check_database_connection(force_refresh: bool = False) -> Dict[str, Any]:
    """Verifies database connectivity and returns connection metadata."""
    active_eng, active_type = resolve_active_engine(force_refresh=force_refresh)

    if active_type == "postgresql":
        return {
            "status": "connected",
            "database_type": "postgresql",
            "active_engine": "postgresql",
            "database_name": settings.DB_NAME,
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "driver": settings.DB_DRIVER,
            "error": None,
            "setup_required": False,
            "setup_instructions": None
        }
    elif active_type == "mysql":
        return {
            "status": "connected",
            "database_type": "postgresql",
            "active_engine": "mysql",
            "database_name": "lenny_growth_assistant",
            "host": "localhost",
            "port": 3306,
            "driver": "mysql+pymysql",
            "error": f"PostgreSQL not detected on port {settings.DB_PORT}; running on active MySQL fallback with all user sessions and knowledge chunks intact.",
            "setup_required": True,
            "setup_instructions": f"PostgreSQL is configured as primary (port {settings.DB_PORT}). Currently active on MySQL fallback (port 3306). Start PostgreSQL service and run 'python scripts/migrate_mysql_to_postgres.py' to switch to PostgreSQL."
        }
    else:
        return {
            "status": "connected",
            "database_type": "sqlite",
            "active_engine": "sqlite",
            "database_name": "lenny_growth_assistant_fallback.db",
            "host": "localhost",
            "port": 0,
            "driver": "sqlite",
            "error": "PostgreSQL and MySQL unavailable; running on local SQLite fallback.",
            "setup_required": True,
            "setup_instructions": "Start MySQL or PostgreSQL service on localhost."
        }
