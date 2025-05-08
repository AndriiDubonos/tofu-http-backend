from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import routers
from .settings.base import Settings
from .sqlalchemy import sqlalchemy_lifespan


def create_app(settings: Settings):
    @asynccontextmanager
    async def lifespan(app_instance: FastAPI):
        async with sqlalchemy_lifespan(app_instance=app_instance, settings=settings):
            yield

    app = FastAPI(lifespan=lifespan)
    app.state.settings = settings

    for router in routers:
        app.include_router(router)

    return app
