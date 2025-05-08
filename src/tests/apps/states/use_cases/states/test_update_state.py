from uuid import uuid4, UUID

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.common.unit_of_work.units.media_storage import MediaStore, InMemoryMediaStorageUnit
from apps.states.data_access.media_storage import StatesMediaStorage
from apps.states.data_access.media_storage.backends.inmemory import InMemoryMediaStorageBackend
from apps.states.use_cases.states.lock_state import LockStateUseCase
from apps.states.use_cases.states.update_state import UpdateStateUseCase
from apps.states.tables.state import State as StateTable
from apps.states.tables.state_version import StateVersion as StateVersionTable
from tests.setupers.unit_of_work import get_active_unit_of_work


async def _assert_state_exists(session: AsyncSession, state_name: str) -> tuple[StateTable, StateVersionTable]:
    stmt = (
        select(StateTable, StateVersionTable)
        .filter_by(name=state_name)
        .join(StateVersionTable, StateTable.latest_version == StateVersionTable.id)
    )
    state, state_version = (await session.execute(stmt)).first()

    assert state is not None
    return state, state_version


def _generate_raw_state_data(version: int = 1) -> bytes:
    raw_data = b'{"version":<version>,"terraform_version":"1.9.1","serial":1,"lineage":"2fbf9278-4e7b-1228-9f69-d27ce621d75b","outputs":{},"resources":[{"mode":"managed","type":"null_resource","name":"example","provider":"provider[\\"registry.opentofu.org/hashicorp/null\\"]","instances":[{"schema_version":0,"attributes":{"id":"588398148598976215","triggers":{"always_run":"2025-05-07T16:24:13Z"}},"sensitive_attributes":[]}]}],"check_results":null}\n'
    return raw_data.replace(b'<version>', f'{version}'.encode('utf8'))


async def _create_and_lock_state(active_transaction_session: AsyncSession, state_name: str, lock_id: UUID) -> None:
    # It would be good to have a separate setuper which would be responsible for
    #  state creation. But it's a bit too much time.
    async with get_active_unit_of_work(active_db_session=active_transaction_session) as uow:
        use_case = LockStateUseCase(unit_of_work=uow, error_class=Exception)
        await use_case.execute(state_name=state_name, lock_id=lock_id)


async def _execute(active_transaction_session: AsyncSession, state_name: str = None, raw_state_data: bytes = None, lock_id: UUID = None) -> MediaStore:
    state_name = state_name or "state_name"
    raw_state_data = raw_state_data or _generate_raw_state_data()

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
    lock_id = uuid4()
    await _create_and_lock_state(
        active_transaction_session=active_transaction_session,
        state_name="state_name",
        lock_id=lock_id,
    )
    await _execute(
        active_transaction_session=active_transaction_session,
        state_name="state_name",
        raw_state_data=_generate_raw_state_data(version=1),
        lock_id=lock_id,
    )
    previous_state, previous_state_version = await _assert_state_exists(session=active_transaction_session, state_name="state_name")
    assert previous_state_version.version == 1

    # save once more
    await _execute(
        active_transaction_session=active_transaction_session,
        state_name="state_name",
        raw_state_data=_generate_raw_state_data(version=2),
        lock_id=lock_id,
    )
    state, state_version = await _assert_state_exists(session=active_transaction_session, state_name="state_name")

    assert state.id == previous_state.id
    assert state.latest_version != previous_state_version.id
    assert state.latest_version == state_version.id
    assert state_version.version == 2


@pytest.mark.asyncio
async def test_upload_state_to_media_store(
        active_transaction_session: AsyncSession,
):
    lock_id = uuid4()
    await _create_and_lock_state(
        active_transaction_session=active_transaction_session,
        state_name="state_name",
        lock_id=lock_id,
    )
    raw_state_data = _generate_raw_state_data()
    media_store = await _execute(active_transaction_session=active_transaction_session, state_name="state_name", lock_id=lock_id)
    state, state_version = await _assert_state_exists(session=active_transaction_session, state_name="state_name")
    assert media_store.get(state_version.path) == raw_state_data
