from uuid import UUID

from domain_model.unit_of_work.unit_of_work import UnitOfWork

from apps.common.logging import default_logger
from apps.states.data_access.media_storage import StatesMediaStorage, get_default_states_media_storage
from apps.states.data_access.repositories.state.repo import StateRepository
from apps.states.domain.states.update_state import update_state


class UpdateStateUseCase:
    def __init__(self, unit_of_work: UnitOfWork, states_media_storage: StatesMediaStorage = None):
        self._unit_of_work = unit_of_work

        self._media_storage = states_media_storage or get_default_states_media_storage(unit_of_work=unit_of_work)

    async def execute(self, state_name: str, raw_state_data: bytes, lock_id: UUID) -> None:
        try:
            await self._execute(state_name=state_name, raw_state_data=raw_state_data, lock_id=lock_id)
        except Exception as e:
            default_logger.error(e)
            raise e
        else:
            default_logger.info(f"State '{state_name}' was updated successfully. Lock ID: {lock_id}.")

    async def _execute(self, state_name: str, raw_state_data: bytes, lock_id: UUID) -> None:
        repo = StateRepository(unit_of_work=self._unit_of_work)
        state = await repo.get_state(state_name=state_name, lock=True)

        state = update_state(state=state, raw_state_data=raw_state_data, lock_id=lock_id)

        await repo.save(state=state)
        await self._media_storage.store(path=state.latest_version.path, raw_state_data=raw_state_data)
