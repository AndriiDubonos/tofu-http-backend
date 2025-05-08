from uuid import UUID

from domain_model.unit_of_work.unit_of_work import UnitOfWork

from apps.states.data_access.media_storage import StatesMediaStorage, get_default_states_media_storage


class UpdateStateUseCase:
    def __init__(self, unit_of_work: UnitOfWork, error_class: type[Exception], states_media_storage: StatesMediaStorage = None):
        self._unit_of_work = unit_of_work
        self._error_class = error_class

        self._media_storage = states_media_storage or get_default_states_media_storage(unit_of_work=unit_of_work)

    async def execute(self, state_name: str, raw_state_data: bytes, lock_id: UUID) -> None:
        pass
