from app.config import Settings


def test_config_defaults():
    # Since we can't easily mock the global instantiation without a patch,
    # we just test a fresh instance with required fields mocked.
    import os

    os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost/db"
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    os.environ["JWT_SECRET_KEY"] = "supersecret"

    settings = Settings()

    assert settings.APP_NAME == "Research Copilot"
    assert settings.ENVIRONMENT == "development"
    assert settings.LOG_LEVEL == "INFO"
    assert settings.DATABASE_URL == "postgresql+asyncpg://user:pass@localhost/db"
    assert settings.REDIS_URL == "redis://localhost:6379/0"
    assert settings.JWT_SECRET_KEY == "supersecret"
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_TTL_MINUTES == 15
    assert settings.REFRESH_TOKEN_TTL_DAYS == 7
    assert "http://localhost:5173" in settings.CORS_ORIGINS
    assert settings.UPLOAD_MAX_BYTES == 26214400
    assert settings.UPLOAD_MAX_PAGES == 500
    assert settings.UPLOAD_DIR == "/data/uploads"
    assert settings.EMBEDDING_PROVIDER == "mock"
    assert settings.EMBEDDING_MODEL == "sentence-transformers/all-MiniLM-L6-v2"
    assert settings.EMBEDDING_DIM == 384
    assert settings.LLM_PROVIDER == "mock"
    assert settings.OPENAI_API_KEY is None
    assert settings.OPENAI_BASE_URL == "https://api.openai.com/v1"
    assert settings.LLM_MODEL == "gpt-4o-mini"
    assert settings.LLM_TIMEOUT_SECONDS == 60
    assert settings.RATE_LIMIT_PER_MINUTE == 120
    assert settings.AUTH_RATE_LIMIT_PER_MINUTE == 5
    assert settings.WORKER_ENABLED is True
    assert settings.METRICS_ENABLED is True
    assert settings.SEED_ON_STARTUP is False


def test_config_overrides(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Test App")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/1")
    monkeypatch.setenv("JWT_SECRET_KEY", "newsecret")

    settings = Settings()

    assert settings.APP_NAME == "Test App"
    assert settings.DATABASE_URL == "sqlite+aiosqlite:///:memory:"
    assert settings.REDIS_URL == "redis://localhost:6379/1"
    assert settings.JWT_SECRET_KEY == "newsecret"
