import alembic.config
import pytest_asyncio

from tofu_http_backend.settings.testing import settings as testing_settings


@pytest_asyncio.fixture(scope="session")
def fastapi_app():
    from tofu_http_backend.app import create_app

    app = create_app(settings=testing_settings)

    # Apply migrations to test db
    db_url_arg = f'dburl={testing_settings.postgres_db}'
    alembic.config.main(argv=['-x', db_url_arg, 'upgrade', 'head'])
    # Rollback after each connect_db from before_server_start
    yield app

    # Rollback db
    alembic.config.main(argv=['-x', db_url_arg, 'downgrade', 'base'])
