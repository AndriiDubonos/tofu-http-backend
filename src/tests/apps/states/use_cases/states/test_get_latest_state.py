import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.common.unit_of_work.units.media_storage import MediaStore, InMemoryMediaStorageUnit
from apps.states.data_access.media_storage import StatesMediaStorage
from apps.states.data_access.media_storage.backends.inmemory import InMemoryMediaStorageBackend
from apps.states.use_cases.states.get_latest_state import GetLatestStateUseCase
from tests.setupers.state.setuper import StateSetuper
from tests.setupers.unit_of_work import get_active_unit_of_work


async def _execute(
    active_transaction_session: AsyncSession,
    state_name: str = "test_state",
    media_store: MediaStore = None,
) -> None | bytes:
    async with get_active_unit_of_work(active_db_session=active_transaction_session, media_storage_unit=InMemoryMediaStorageUnit(storage=media_store)) as uow:
        states_media_storage = StatesMediaStorage(InMemoryMediaStorageBackend(unit_of_work=uow))
        use_case = GetLatestStateUseCase(unit_of_work=uow, error_class=Exception, states_media_storage=states_media_storage)
        return await use_case.execute(state_name=state_name)



@pytest.mark.asyncio
async def test_get_latest_state_for_existing_state(
        active_transaction_session: AsyncSession,
):
    setuper = StateSetuper(session=active_transaction_session)

    state_name = "test_state"
    raw_state_data = setuper.generate_raw_state_data(version=1)
    media_store = MediaStore()

    # Create a state with a version
    await setuper.create_state(state_name)
    await setuper.add_state_version(state_name, version=1)
    
    # Store the raw state data in the media store
    state, version = await setuper.get_state(state_name)
    media_store.add(version.path, raw_state_data)

    result = await _execute(
        active_transaction_session=active_transaction_session,
        state_name=state_name,
        media_store=media_store,
    )

    assert result == raw_state_data


@pytest.mark.asyncio
async def test_get_latest_state_for_non_existing_state(
        active_transaction_session: AsyncSession,
):
    result = await _execute(active_transaction_session=active_transaction_session)
    
    # Should return None for non-existent state
    assert result is None


@pytest.mark.asyncio
async def test_get_latest_state_for_state_without_version(
        active_transaction_session: AsyncSession,
):
    # Create a state without a version using the setuper
    state_name = "state_without_version"
    setuper = StateSetuper(session=active_transaction_session)
    await setuper.create_state(state_name)

    # Verify the state exists but has no version
    state, version = await setuper.get_state(state_name)
    assert state is not None
    assert state.latest_version is None
    assert version is None

    result = await _execute(active_transaction_session=active_transaction_session, state_name=state_name)

    assert result is None
