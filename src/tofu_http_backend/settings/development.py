from tofu_http_backend.settings.base import Settings

settings: Settings = Settings(postgres_db='postgresql+asyncpg://user:password@postgres:5432/tofu_http_backend_db')
