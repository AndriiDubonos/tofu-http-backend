from tofu_http_backend.settings.base import Settings

settings: Settings = Settings(postgres_db='postgresql+asyncpg://user:password@postgres:5432/test_tofu_http_backend_db')
