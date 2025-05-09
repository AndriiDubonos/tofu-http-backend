from uuid import UUID

from domain_model.unit_of_work.unit_of_work import UnitOfWork

from apps.states.data_access.repositories.state.repo import StateRepository
from apps.states.domain.states.lock_state import lock_state


class LockStateUseCase:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    async def execute(self, state_name: str, lock_id: UUID) -> None:
        repo = StateRepository(unit_of_work=self._unit_of_work)
        state = await repo.get_state(state_name=state_name, lock=True)

        state = lock_state(state=state, lock_id=lock_id)

        await repo.save(state=state)
