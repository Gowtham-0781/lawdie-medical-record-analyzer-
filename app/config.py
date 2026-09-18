from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Lawdie Medical Record Analyzer"
    app_env: str = "development"

    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"

    chunk_size: int = 1200
    chunk_overlap: int = 200
    top_k: int = 6

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()