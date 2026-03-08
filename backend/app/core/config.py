from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM providers
    groq_api_key: str = ""
    google_api_key: str = ""
    mistral_api_key: str = ""

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "documents"

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    # Memory
    sqlite_db_path: str = "memory.db"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Default active LLM provider
    default_provider: str = "groq"


settings = Settings()
