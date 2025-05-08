from apps.states.data_access.media_storage.backends.base import BaseMediaStorageBackend


class StatesMediaStorage:
    def __init__(self, backend: BaseMediaStorageBackend):
        self._backend = backend

    def store(self, path: str, raw_state_data: bytes) -> None:
        self._backend.store(path=path, raw_state_data=raw_state_data)

    def retrieve(self, path: str) -> bytes:
        return self._backend.retrieve(path=path)
