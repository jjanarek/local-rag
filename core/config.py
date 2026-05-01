from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized configuration for the Local RAG project.
    Values are loaded with the following priority:
    1. Environment variables
    2. .env file
    3. defaults provided below
    """

    # API Settings
    APP_NAME: str = "Local RAG API"
    DEBUG: bool = True
    CORS_ORIGINS: list[str] = ["http://localhost:8501", "http://localhost:3000"]

    # Vector DB
    QDRANT_URL: str = "http://localhost:6333"
    COLLECTION_NAME: str = "local_rag_docs"

    # LLM & Embeddings
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    LLM_MODEL: str = "llama3"

    # File limits
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB default

    # Vector Search
    MIN_SCORE: float = 0.4
    MAX_NUMBER_OF_HITS: int = 5

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )


settings = Settings()
