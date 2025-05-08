import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from apps.common.unit_of_work.units.media_storage import MediaStore, InMemoryMediaStorageUnit
from apps.states.data_access.media_storage import StatesMediaStorage
from apps.states.data_access.media_storage.backends.inmemory import InMemoryMediaStorageBackend
from apps.states.use_cases.states.update_state import UpdateStateUseCase
from tests.setupers.state.setuper import StateSetuper
from tests.setupers.unit_of_work import get_active_unit_of_work


async def _execute(
    active_transaction_session: AsyncSession,
    state_name: str = "state_name",
    raw_state_data: bytes = None,
    lock_id: uuid4 = None,
) -> MediaStore:
    setuper = StateSetuper(session=active_transaction_session)
    raw_state_data = raw_state_data or setuper.generate_raw_state_data()

    media_store = MediaStore()
    media_unit = InMemoryMediaStorageUnit(storage=media_store)

    async with get_active_unit_of_work(active_db_session=active_transaction_session, media_storage_unit=media_unit) as uow:
        states_media_storage = StatesMediaStorage(InMemoryMediaStorageBackend(unit_of_work=uow))
        use_case = UpdateStateUseCase(unit_of_work=uow, error_class=Exception, states_media_storage=states_media_storage)
        await use_case.execute(state_name=state_name, raw_state_data=raw_state_data, lock_id=lock_id or uuid4())

    return media_store


@pytest.mark.asyncio
async def test_update_state_for_not_existing_state(
        active_transaction_session: AsyncSession,
):
    with pytest.raises(Exception, match="State state_name is not locked and can't be updated."):
        await _execute(active_transaction_session=active_transaction_session, state_name="state_name")


@pytest.mark.asyncio
async def test_update_state_for_already_existing_locked_state(
        active_transaction_session: AsyncSession,
):
    setuper = StateSetuper(session=active_transaction_session)
    state_name = "state_name"
    lock_id = uuid4()

    await setuper.create_state(state_name)
    await setuper.lock_state(state_name, lock_id)

    await _execute(
        active_transaction_session=active_transaction_session,
        state_name=state_name,
        lock_id=lock_id,
    )

    previous_state, previous_state_version = await setuper.get_state(state_name=state_name)
    assert previous_state_version.version == 1


@pytest.mark.asyncio
async def test_update_state_when_another_version_already_exists(
        active_transaction_session: AsyncSession,
):
    setuper = StateSetuper(session=active_transaction_session)
    state_name = "state_name"
    lock_id = uuid4()

    await setuper.create_state(state_name)
    previous_version_id = await setuper.add_state_version(state_name=state_name, version=1)
    await setuper.lock_state(state_name=state_name, lock_id=lock_id)

    raw_state_data_v2 = setuper.generate_raw_state_data(version=2)
    await _execute(
        active_transaction_session=active_transaction_session,
        state_name=state_name,
        raw_state_data=raw_state_data_v2,
        lock_id=lock_id,
    )

    state, state_version = await setuper.get_state(state_name=state_name)
    assert state.latest_version != previous_version_id
    assert state.latest_version == state_version.id
    assert state_version.version == 2


@pytest.mark.asyncio
async def test_upload_state_to_media_store(
        active_transaction_session: AsyncSession,
):
    setuper = StateSetuper(session=active_transaction_session)
    state_name = "state_name"
    lock_id = uuid4()

    await setuper.create_state(state_name)
    await setuper.lock_state(state_name, lock_id)
    
    # Update the state
    raw_state_data = setuper.generate_raw_state_data()
    media_store = await _execute(
        active_transaction_session=active_transaction_session,
        state_name=state_name,
        raw_state_data=raw_state_data,
        lock_id=lock_id
    )
    
    # Verify the state was uploaded to media store
    state, state_version = await setuper.get_state(state_name=state_name)
    assert media_store.get(state_version.path) == raw_state_data
