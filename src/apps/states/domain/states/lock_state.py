from uuid import UUID

from apps.states.domain.states.errors import ConcurrentLockError
from apps.states.models.state import State


def lock_state(state: State, lock_id: UUID) -> State:
    # Check if state is already locked
    if state.lock_id is not None:
        raise ConcurrentLockError(f"State '{state.name}' is already locked with lock ID: {state.lock_id}")
    
    # Set the lock ID
    state.lock_id = lock_id
    return state
