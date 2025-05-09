from pydantic import BaseModel
from pydantic_settings import BaseSettings


class MinioSettings(BaseModel):
    host: str
    access_key: str
    secret_key: str


class Settings(BaseSettings):
    postgres_db: str
    minio: MinioSettings | None
