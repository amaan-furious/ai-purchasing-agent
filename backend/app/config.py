from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    OPENAI_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./purchasing.db"
    LLM_MODEL: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
