import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from apps.states.domain.states.errors import ConcurrentLockError
from apps.states.use_cases.states.lock_state import LockStateUseCase
from tests.setupers.state.setuper import StateSetuper
from tests.setupers.unit_of_work import get_active_unit_of_work


async def _execute(
    active_transaction_session: AsyncSession,
    state_name: str,
    lock_id=None,
) -> None:
    lock_id = lock_id or uuid4()

    async with get_active_unit_of_work(
        active_db_session=active_transaction_session
    ) as uow:
        use_case = LockStateUseCase(unit_of_work=uow)
        await use_case.execute(state_name=state_name, lock_id=lock_id)

    return lock_id


@pytest.mark.asyncio
async def test_lock_state_for_non_existing_state(
    active_transaction_session: AsyncSession,
):
    state_name = "non_existing_state"
    lock_id = uuid4()

    await _execute(
        active_transaction_session=active_transaction_session,
        state_name=state_name,
        lock_id=lock_id,
    )

    setuper = StateSetuper(session=active_transaction_session)
    state, _ = await setuper.get_state(state_name=state_name)

    assert state is not None
    assert state.lock_id == lock_id


@pytest.mark.asyncio
async def test_lock_state_for_existing_unlocked_state(
    active_transaction_session: AsyncSession,
):
    setuper = StateSetuper(session=active_transaction_session)
    state_name = "existing_unlocked_state"

    # Create the state without locking it
    await setuper.create_state(state_name=state_name)

    lock_id = await _execute(
        active_transaction_session=active_transaction_session,
        state_name=state_name,
    )

    state, _ = await setuper.get_state(state_name=state_name)
    assert state.lock_id == lock_id


@pytest.mark.asyncio
async def test_lock_state_for_already_locked_state(
    active_transaction_session: AsyncSession,
):
    setuper = StateSetuper(session=active_transaction_session)
    state_name = "already_locked_state"
    original_lock_id = uuid4()

    await setuper.create_state(state_name=state_name)
    await setuper.lock_state(state_name=state_name, lock_id=original_lock_id)

    new_lock_id = uuid4()
    with pytest.raises(
        ConcurrentLockError,
        match=f"State '{state_name}' is already locked with lock ID: {original_lock_id}",
    ):
        await _execute(
            active_transaction_session=active_transaction_session,
            state_name=state_name,
            lock_id=new_lock_id,
        )

    # Verify the state still has the original lock ID
    state, _ = await setuper.get_state(state_name=state_name)
    assert state.lock_id == original_lock_id
