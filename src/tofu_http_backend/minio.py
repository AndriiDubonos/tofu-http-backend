from contextlib import asynccontextmanager

from fastapi import FastAPI
from minio import Minio

from tofu_http_backend.settings.base import Settings


@asynccontextmanager
async def minio_lifespan(app_instance: FastAPI, settings: Settings):
    client = Minio(
        endpoint=settings.minio.host,
        access_key=settings.minio.access_key,
        secret_key=settings.minio.secret_key,
        secure=False,
    )

    app_instance.state.minio_client = client

    yield

    # not found any docs how to correctly close minio client
    app_instance.state.minio_client = None
    del client
