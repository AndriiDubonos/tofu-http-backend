from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import routers
from .sqlalchemy import sqlalchemy_lifespan


def create_app():
    @asynccontextmanager
    async def lifespan(app_instance: FastAPI):
        async with sqlalchemy_lifespan(app_instance=app_instance):
            yield

    app = FastAPI(lifespan=lifespan)

    for router in routers:
        app.include_router(router)

    return app
