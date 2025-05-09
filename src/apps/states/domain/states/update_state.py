from json import loads
from uuid import UUID
from hashlib import sha256

from domain_model.object_id import ObjectID

from apps.states.domain.states.errors import ConcurrentLockError, MissingLockError
from apps.states.models.state import StateVersion, State


def update_state(state: State, raw_state_data: bytes, lock_id: UUID) -> State:
    if state.lock_id is None:
        raise MissingLockError(f"State {state.name} is not locked and can't be updated.")
    if state.lock_id != lock_id:
        raise ConcurrentLockError(f"State {state.name} is locked by another user.")

    state_version_id = ObjectID(id_=None)
    new_state_version = StateVersion(
        id=state_version_id,
        version=loads(raw_state_data.decode('utf8'))['version'],
        hash=_get_hash(raw_state_data=raw_state_data),
        path=_generate_path_for_state(state=state, state_version_id=state_version_id.value)
    )
    state.latest_version = new_state_version
    return state


def _get_hash(raw_state_data: bytes) -> str:
    m = sha256()
    m.update(raw_state_data)
    return m.hexdigest()


def _generate_path_for_state(state: State, state_version_id: UUID):
    return f'{state.id.value}/versions/{state_version_id}.json'
