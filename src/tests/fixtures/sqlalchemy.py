import pytest_asyncio


@pytest_asyncio.fixture  # TODO: scope='session'
def database_sessionmaker(fastapi_app):
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(fastapi_app.state.settings.postgres_db, echo=False)
    yield sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
def database_session(database_sessionmaker):
    yield database_sessionmaker(autobegin=False)


@pytest_asyncio.fixture
async def active_transaction_session(database_session):
    async with database_session.begin() as transaction:
        yield database_session
        await transaction.rollback()
