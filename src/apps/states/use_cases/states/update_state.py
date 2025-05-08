from json import loads
from uuid import UUID
from hashlib import sha256

from domain_model.object_id import ObjectID
from domain_model.unit_of_work.unit_of_work import UnitOfWork

from apps.states.data_access.media_storage import StatesMediaStorage, get_default_states_media_storage
from apps.states.data_access.repositories.state.repo import StateRepository
from apps.states.models.state import StateVersion, State


class UpdateStateUseCase:
    def __init__(self, unit_of_work: UnitOfWork, error_class: type[Exception], states_media_storage: StatesMediaStorage = None):
        self._unit_of_work = unit_of_work
        self._error_class = error_class

        self._media_storage = states_media_storage or get_default_states_media_storage(unit_of_work=unit_of_work)

    async def execute(self, state_name: str, raw_state_data: bytes, lock_id: UUID) -> None:
        repo = StateRepository(unit_of_work=self._unit_of_work)
        state = await repo.get_state(state_name=state_name)

        state_version_id = ObjectID(id_=None)
        new_state_version = StateVersion(
            id=state_version_id,
            version=loads(raw_state_data.decode('utf8'))['version'],
            hash=self._get_hash(raw_state_data=raw_state_data),
            path=self._generate_path_for_state(state=state, state_version_id=state_version_id.value)
        )

        state.latest_version = new_state_version
        await repo.save(state=state)
        self._media_storage.store(path=new_state_version.path, raw_state_data=raw_state_data)

    def _get_hash(self, raw_state_data: bytes) -> str:
        m = sha256()
        m.update(raw_state_data)
        return m.hexdigest()

    def _generate_path_for_state(self, state: State, state_version_id: UUID):
        return f'{state.id.value}/versions/{state_version_id}.json'
