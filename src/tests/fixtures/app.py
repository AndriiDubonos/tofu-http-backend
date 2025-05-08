import asyncio

import alembic.config
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from tofu_http_backend.settings.testing import settings as testing_settings


@pytest_asyncio.fixture(scope="session")
def fastapi_app():
    from tofu_http_backend.app import create_app

    app = create_app(settings=testing_settings)

    # Apply migrations to test db
    asyncio.run(create_database(testing_settings.postgres_db))

    db_url_arg = f'dburl={testing_settings.postgres_db}'
    alembic.config.main(argv=['-x', db_url_arg, 'upgrade', 'head'])
    # Rollback after each connect_db from before_server_start
    yield app

    # Rollback db
    alembic.config.main(argv=['-x', db_url_arg, 'downgrade', 'base'])


async def create_database(postgres_db: str):
    db_host, db_name = postgres_db.rsplit('/', maxsplit=1)
    engine = create_async_engine(f'{db_host}/postgres')
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name};"))
        await conn.execute(text(f"CREATE DATABASE {db_name};"))
