from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Groq Configuration
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    
    # OpenAI Configuration
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    
    # Supabase Configuration
    supabase_url: str
    supabase_service_role_key: str
    
    # Document Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Vector Search
    similarity_top_k: int = 4
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
