from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from tofu_http_backend.settings.base import Settings

mainmetatadata = MetaData()
Base = declarative_base(metadata=mainmetatadata)


@asynccontextmanager
async def sqlalchemy_lifespan(app_instance: FastAPI, settings: Settings):
    engine = create_async_engine(settings.postgres_db)

    app_instance.state.session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    yield
    await engine.dispose()
