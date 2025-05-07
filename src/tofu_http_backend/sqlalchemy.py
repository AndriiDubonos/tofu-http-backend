from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .settings import settings


@asynccontextmanager
async def sqlalchemy_lifespan(app_instance: FastAPI):
    engine = create_async_engine(settings.postgres_db)
    app_instance.state.session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    yield
    await engine.dispose()
