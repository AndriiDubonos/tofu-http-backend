from io import BytesIO
from typing import cast

from minio import Minio

from apps.common.unit_of_work.unit_type import UnitType
from apps.common.unit_of_work.units.media_storage import MinIOMediaStorageUnit
from apps.states.data_access.media_storage.backends.base import BaseMediaStorageBackend


class MinIOMediaStorageBackend(BaseMediaStorageBackend):
    async def _get_client(self) -> Minio:
        unit = cast(
            MinIOMediaStorageUnit,
            await self._unit_of_work.get_unit(unit_type=UnitType.MEDIA_STORAGE),
        )
        return unit.get_client()

    async def store(self, path: str, raw_state_data: bytes) -> None:
        client = await self._get_client()
        client.put_object(
            bucket_name="states",
            object_name=path,
            data=BytesIO(raw_state_data),
            length=len(raw_state_data),
        )

    async def retrieve(self, path: str) -> bytes:
        client = await self._get_client()
        response = None
        try:
            response = client.get_object("states", path)

            if response.status != 200:
                raise Exception(
                    f"Unexpected response {response.status}: `{response.data}"
                )

            return response.data
        finally:
            if response:
                response.close()
                response.release_conn()
