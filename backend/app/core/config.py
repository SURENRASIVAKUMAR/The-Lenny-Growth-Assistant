import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "The Lenny Growth Assistant"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    
    # Database Configuration (PostgreSQL primary)
    DB_DRIVER: str = "postgresql+psycopg2"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "lenny_growth_assistant"
    DATABASE_URL: Optional[str] = None
    
    # Preserved MySQL URL for reading/migrating existing user data
    MYSQL_DATABASE_URL: Optional[str] = "mysql+pymysql://root:@localhost:3306/lenny_growth_assistant"
    
    # AI Provider Configuration
    # Options: "ollama", "openai", "demo"
    AI_PROVIDER: str = "ollama"
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:latest"
    OLLAMA_TIMEOUT_SECONDS: int = 60
    
    # Authoritative Repository Settings
    AUTHORITATIVE_REPO_PATH: str = "data/lennys-podcast-transcripts"
    
    # Strict Grounding & RAG Settings
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 120
    RAG_TOP_K: int = 5
    MIN_EVIDENCE_THRESHOLD: float = 0.14  # Balanced threshold preventing hallucinations while supporting multi-token queries
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        pwd = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return f"{self.DB_DRIVER}://{self.DB_USER}{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
