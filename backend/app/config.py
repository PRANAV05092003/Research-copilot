
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Research Copilot"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str
    REDIS_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_TTL_MINUTES: int = 15
    REFRESH_TOKEN_TTL_DAYS: int = 7

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost"]

    UPLOAD_MAX_BYTES: int = 26214400 # 25MB
    UPLOAD_MAX_PAGES: int = 500
    UPLOAD_DIR: str = "/data/uploads"

    EMBEDDING_PROVIDER: str = "mock"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    LLM_PROVIDER: str = "mock"
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TIMEOUT_SECONDS: int = 60

    RATE_LIMIT_PER_MINUTE: int = 120
    AUTH_RATE_LIMIT_PER_MINUTE: int = 5

    WORKER_ENABLED: bool = True
    METRICS_ENABLED: bool = True
    SEED_ON_STARTUP: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def validate_production_providers(self) -> "Settings":
        if self.ENVIRONMENT == "production":
            if self.LLM_PROVIDER == "mock":
                raise ValueError("LLM_PROVIDER cannot be 'mock' in production environment.")
            if self.EMBEDDING_PROVIDER == "mock":
                raise ValueError("EMBEDDING_PROVIDER cannot be 'mock' in production environment.")
        return self

settings = Settings() # type: ignore
