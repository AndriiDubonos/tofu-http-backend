from domain_model.unit_of_work.unit_of_work import UnitOfWork

from apps.states.data_access.media_storage import StatesMediaStorage, get_default_states_media_storage
from apps.states.data_access.repositories.state.repo import StateRepository


class GetLatestStateUseCase:
    def __init__(self, unit_of_work: UnitOfWork, states_media_storage: StatesMediaStorage = None):
        self._unit_of_work = unit_of_work

        self._media_storage = states_media_storage or get_default_states_media_storage(unit_of_work=unit_of_work)

    async def execute(self, state_name: str) -> bytes | None:
        repo = StateRepository(unit_of_work=self._unit_of_work)
        state = await repo.get_state(state_name=state_name, lock=False)
        
        if state.id.is_new or state.latest_version is None:
            return None
        
        return await self._media_storage.retrieve(state.latest_version.path)
