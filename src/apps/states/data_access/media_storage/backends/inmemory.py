from typing import cast

from apps.common.unit_of_work.unit_type import UnitType
from apps.common.unit_of_work.units.media_storage import (
    InMemoryMediaStorageUnit,
    MediaStore,
)
from apps.states.data_access.media_storage.backends.base import BaseMediaStorageBackend


class InMemoryMediaStorageBackend(BaseMediaStorageBackend):
    async def _get_media_storage(self) -> MediaStore:
        media_storage_unit = cast(
            InMemoryMediaStorageUnit,
            await self._unit_of_work.get_unit(UnitType.MEDIA_STORAGE),
        )
        return media_storage_unit.get_storage()

    async def store(self, path: str, raw_state_data: bytes) -> None:
        storage = await self._get_media_storage()
        storage.add(path=path, value=raw_state_data)

    async def retrieve(self, path: str) -> bytes:
        storage = await self._get_media_storage()
        return storage.get(path=path)
