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
    qdrant_api_key: str = ""

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    # Memory
    sqlite_db_path: str = "memory.db"

    # CORS — comma-separated string instead of list to avoid JSON parsing issues
    cors_origins: str = "http://localhost:3000"

    # Default active LLM provider
    default_provider: str = "groq"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
