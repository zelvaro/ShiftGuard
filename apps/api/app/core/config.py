from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ShiftGuard API"
    environment: str = "dev"
    cors_origins: list[str] = ["http://localhost:3000"]

    database_url: str = "postgresql+psycopg://shiftguard:shiftguard@localhost:5432/shiftguard"
    redis_url: str = "redis://localhost:6379/0"

    # WhatsApp Cloud API (Meta)
    whatsapp_verify_token: str = "change-me"
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_api_version: str = "v23.0"

    # IA : fournisseur LLM + transcription (Groq, OpenAI, Anthropic...)
    llm_provider: str = "groq"
    llm_api_key: str = ""
    llm_model: str = ""
    stt_model: str = "whisper-large-v3"


@lru_cache
def get_settings() -> Settings:
    return Settings()
