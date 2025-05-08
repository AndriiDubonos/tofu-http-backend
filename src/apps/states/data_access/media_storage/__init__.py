from domain_model.unit_of_work.unit_of_work import UnitOfWork

from .backends.minio import MinIOMediaStorageBackend
from .media_storage import StatesMediaStorage


def get_default_states_media_storage(unit_of_work: UnitOfWork) -> StatesMediaStorage:
    return StatesMediaStorage(backend=MinIOMediaStorageBackend(unit_of_work=unit_of_work))
