from domain_model.unit_of_work.units.base import BaseUnit
from minio import Minio


class BaseMediaStorageUnit(BaseUnit):
    async def handle_exception(self, exc_type, exc_val, exc_tb):
        # media storages are not transactional
        pass


class MediaStore:
    def __init__(self):
        self._container = {}

    def add(self, path: str, value: bytes) -> None:
        self._container[path] = value

    def get(self, path: str) -> bytes | None:
        return self._container.get(path)


class InMemoryMediaStorageUnit(BaseMediaStorageUnit):
    def __init__(self, storage: MediaStore):
        super().__init__()
        self._storage = storage

    def get_storage(self) -> MediaStore:
        return self._storage


class MinIOMediaStorageUnit(BaseMediaStorageUnit):
    def __init__(self, client: Minio):
        super().__init__()
        self._client = client

    def get_client(self) -> Minio:
        return self._client
