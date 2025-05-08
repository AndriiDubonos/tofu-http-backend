from apps.states.data_access.media_storage.backends.base import BaseMediaStorageBackend


class StatesMediaStorage:
    def __init__(self, backend: BaseMediaStorageBackend):
        self._backend = backend

    async def store(self, path: str, raw_state_data: bytes) -> None:
        await self._backend.store(path=path, raw_state_data=raw_state_data)

    async def retrieve(self, path: str) -> bytes:
        return await self._backend.retrieve(path=path)
