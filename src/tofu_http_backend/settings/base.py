from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
