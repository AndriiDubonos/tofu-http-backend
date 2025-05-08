from apps.states.data_access.media_storage.backends.base import BaseMediaStorageBackend


class MinIOMediaStorageBackend(BaseMediaStorageBackend):
    async def store(self, path: str, raw_state_data: bytes) -> None:
        raise ValueError

    async def retrieve(self, path: str) -> bytes:
        raise ValueError
