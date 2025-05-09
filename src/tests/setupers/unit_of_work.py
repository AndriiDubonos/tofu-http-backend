from domain_model.unit_of_work.unit_of_work import UnitOfWork
from domain_model.unit_of_work.units.base import BaseUnit
from domain_model.unit_of_work.units.db.contrib.sqlalchemy import (
    SQLAlchemyActiveTransactionSessionDBUnit,
)
from sqlalchemy.ext.asyncio import AsyncSession

from apps.common.unit_of_work.unit_type import UnitType
from apps.common.unit_of_work.units.media_storage import (
    InMemoryMediaStorageUnit,
    MediaStore,
)


def get_test_unit_of_work(
    db_unit: BaseUnit,
    media_storage_unit: BaseUnit,
) -> UnitOfWork:
    return UnitOfWork(
        units={
            UnitType.DATABASE: db_unit,
            UnitType.MEDIA_STORAGE: media_storage_unit,
        }
    )


def get_active_unit_of_work(
    active_db_session: AsyncSession,
    media_storage_unit: BaseUnit = None,
):
    return get_test_unit_of_work(
        db_unit=SQLAlchemyActiveTransactionSessionDBUnit(session=active_db_session),
        media_storage_unit=media_storage_unit
        or InMemoryMediaStorageUnit(storage=MediaStore()),
    )
