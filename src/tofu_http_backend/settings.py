from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str


settings: Settings = Settings(postgres_db='asyncpg://user:password@postgres:5432/tofu_http_backend_db')
