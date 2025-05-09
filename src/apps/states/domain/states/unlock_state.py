from uuid import UUID

from apps.states.domain.states.errors import ConcurrentLockError
from apps.states.models.state import State


def unlock_state(state: State, lock_id: UUID, force: bool) -> State:
    # Check if state is locked
    if state.lock_id is None:
        raise ConcurrentLockError(f"State '{state.name}' is not locked")
    
    # Check if the lock ID matches or force is True
    if not force and state.lock_id != lock_id:
        raise ConcurrentLockError(f"Cannot unlock state '{state.name}' with lock ID {lock_id}. It is locked with a different ID: {state.lock_id}")
    
    # Clear the lock ID
    state.lock_id = None
    return state
