from domain_model.unit_of_work.unit_of_work import UnitOfWork


class BaseMediaStorageBackend:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    async def store(self, path: str, raw_state_data: bytes) -> None:
        raise NotImplementedError

    async def retrieve(self, path: str) -> bytes:
        raise NotImplementedError
