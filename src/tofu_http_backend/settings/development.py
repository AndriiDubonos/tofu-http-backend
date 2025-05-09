from tofu_http_backend.settings.base import Settings, MinioSettings

settings: Settings = Settings(
    postgres_db='postgresql+asyncpg://user:password@postgres:5432/tofu_http_backend_db',
    minio=MinioSettings(
        host='minio:9000',
        access_key='user',
        secret_key='password',
    ),
)
