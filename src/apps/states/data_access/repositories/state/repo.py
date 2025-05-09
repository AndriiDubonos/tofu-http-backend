from datetime import datetime, UTC
from typing import cast

from domain_model.object_id import ObjectID
from domain_model.unit_of_work.unit_of_work import UnitOfWork
from domain_model.unit_of_work.units.db import BaseDBUnit
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from apps.common.unit_of_work.unit_type import UnitType
from apps.states.models.state import State, StateVersion
from apps.states.tables.state import State as StateTable
from apps.states.tables.state_version import StateVersion as StateVersionTable


class StateLockedError(Exception):
    def __init__(self, message):
        self.message = message


class StateRepository:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work
        # If needed could be extended with different backends

    async def _get_session(self):
        db_unit = cast(BaseDBUnit, await self._unit_of_work.get_unit(UnitType.DATABASE))
        return db_unit.get_db_session()

    async def get_state(self, state_name: str, lock: bool) -> State:
        session = await self._get_session()

        # First, get the state and apply lock if needed
        state_stmt = select(StateTable).filter_by(name=state_name)

        if lock:
            state_stmt = state_stmt.with_for_update(nowait=True)

        try:
            state = (await session.scalars(state_stmt)).first()
        except OperationalError as e:
            if "could not obtain lock" in str(e) or "deadlock detected" in str(e):
                # State exists but is locked
                raise StateLockedError(
                    f"State '{state_name}' is currently locked by another transaction"
                )
            raise

        if state is None:
            return State(
                id=ObjectID(None),
                name=state_name,
                latest_version=None,
                lock_id=None,
            )

        # Then, get the related state version if it exists
        latest_version = None
        if state.latest_version is not None:
            version_stmt = select(StateVersionTable).filter_by(id=state.latest_version)
            latest_version = (await session.scalars(version_stmt)).first()

        return State(
            id=ObjectID(state.id),
            name=state.name,
            lock_id=state.lock_id,
            latest_version=None
            if latest_version is None
            else StateVersion(
                id=ObjectID(latest_version.id),
                version=latest_version.version,
                hash=latest_version.hash,
                path=latest_version.path,
            ),
        )

    async def save(self, state: State):
        db_session = await self._get_session()

        if state.id.is_new:
            state_table = StateTable(id=state.id.value, name=state.name)
            db_session.add(state_table)
        else:
            state_table = await db_session.get(StateTable, state.id.value)
            state_table.modified_date = datetime.now(UTC)

        if state.latest_version is not None and state.latest_version.id.is_new:
            latest_version_table = StateVersionTable(
                id=state.latest_version.id.value,
                state_id=state.id.value,
                version=state.latest_version.version,
                hash=state.latest_version.hash,
                path=state.latest_version.path,
            )
            db_session.add(latest_version_table)

            # needed to populate `StateVersionTable` into DB - so it's possible to use it as FK value
            await db_session.flush()

        state_table.latest_version = (
            state.latest_version.id.value if state.latest_version is not None else None
        )
        state_table.lock_id = state.lock_id
        db_session.add(state_table)

        await db_session.flush()
