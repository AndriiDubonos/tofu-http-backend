import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from apps.states.domain.states.errors import ConcurrentLockError
from apps.states.use_cases.states.unlock_state import UnlockStateUseCase
from tests.setupers.state.setuper import StateSetuper
from tests.setupers.unit_of_work import get_active_unit_of_work


async def _execute(
    active_transaction_session: AsyncSession,
    state_name: str,
    lock_id=None,
    force: bool = False,
) -> None:
    lock_id = lock_id or uuid4()

    async with get_active_unit_of_work(
        active_db_session=active_transaction_session
    ) as uow:
        use_case = UnlockStateUseCase(unit_of_work=uow)
        await use_case.execute(state_name=state_name, lock_id=lock_id, force=force)


@pytest.mark.asyncio
async def test_unlock_state_for_non_existing_state(
    active_transaction_session: AsyncSession,
):
    state_name = "non_existing_state"
    lock_id = uuid4()

    with pytest.raises(
        ConcurrentLockError, match=f"State '{state_name}' is not locked"
    ):
        await _execute(
            active_transaction_session=active_transaction_session,
            state_name=state_name,
            lock_id=lock_id,
        )


@pytest.mark.asyncio
async def test_unlock_state_for_unlocked_state(
    active_transaction_session: AsyncSession,
):
    setuper = StateSetuper(session=active_transaction_session)
    state_name = "unlocked_state"

    await setuper.create_state(state_name=state_name)

    with pytest.raises(
        ConcurrentLockError, match=f"State '{state_name}' is not locked"
    ):
        await _execute(
            active_transaction_session=active_transaction_session,
            state_name=state_name,
            lock_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_unlock_state_with_correct_lock_id(
    active_transaction_session: AsyncSession,
):
    setuper = StateSetuper(session=active_transaction_session)
    state_name = "locked_state"
    lock_id = uuid4()

    await setuper.create_state(state_name=state_name)
    await setuper.lock_state(state_name=state_name, lock_id=lock_id)

    await _execute(
        active_transaction_session=active_transaction_session,
        state_name=state_name,
        lock_id=lock_id,
    )

    state, _ = await setuper.get_state(state_name=state_name)
    assert state.lock_id is None


@pytest.mark.asyncio
async def test_unlock_state_with_incorrect_lock_id(
    active_transaction_session: AsyncSession,
):
    setuper = StateSetuper(session=active_transaction_session)
    state_name = "locked_state_incorrect_id"
    correct_lock_id = uuid4()
    incorrect_lock_id = uuid4()

    await setuper.create_state(state_name=state_name)
    await setuper.lock_state(state_name=state_name, lock_id=correct_lock_id)

    with pytest.raises(
        ConcurrentLockError,
        match=f"Cannot unlock state '{state_name}' with lock ID {incorrect_lock_id}",
    ):
        await _execute(
            active_transaction_session=active_transaction_session,
            state_name=state_name,
            lock_id=incorrect_lock_id,
        )

    state, _ = await setuper.get_state(state_name=state_name)
    assert state.lock_id == correct_lock_id


@pytest.mark.asyncio
async def test_force_unlock_state(
    active_transaction_session: AsyncSession,
):
    setuper = StateSetuper(session=active_transaction_session)
    state_name = "force_unlock_state"
    original_lock_id = uuid4()

    await setuper.create_state(state_name=state_name)
    await setuper.lock_state(state_name=state_name, lock_id=original_lock_id)

    different_lock_id = uuid4()
    await _execute(
        active_transaction_session=active_transaction_session,
        state_name=state_name,
        lock_id=different_lock_id,
        force=True,
    )

    state, _ = await setuper.get_state(state_name=state_name)
    assert state.lock_id is None
