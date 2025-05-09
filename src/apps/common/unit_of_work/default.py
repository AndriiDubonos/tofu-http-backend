from domain_model.unit_of_work.unit_of_work import UnitOfWork
from domain_model.unit_of_work.units.db.contrib.sqlalchemy import SQLAlchemySessionDBUnit
from fastapi import FastAPI

from apps.common.unit_of_work.unit_type import UnitType
from apps.common.unit_of_work.units.media_storage import MinIOMediaStorageUnit


def get_default_unit_of_work(app: FastAPI) -> UnitOfWork:
    return UnitOfWork(
        units={
            UnitType.DATABASE: SQLAlchemySessionDBUnit(session_factory=app.state.session_factory),
            UnitType.MEDIA_STORAGE: MinIOMediaStorageUnit(client=app.state.minio_client),
        }
    )
