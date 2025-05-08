from typing import cast

from domain_model.object_id import ObjectID
from domain_model.unit_of_work.unit_of_work import UnitOfWork
from domain_model.unit_of_work.units.db import BaseDBUnit
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from apps.common.unit_of_work.unit_type import UnitType
from apps.states.models.state import State, StateVersion
from apps.states.tables.state import State as StateTable
from apps.states.tables.state_version import StateVersion as StateVersionTable


class StateRepository:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work
        # If needed could be extended with different backends

    async def _get_session(self):
        db_unit = cast(BaseDBUnit, await self._unit_of_work.get_unit(UnitType.DATABASE))
        return db_unit.get_db_session()

    async def get_state(self, state_name: str) -> State:
        session = await self._get_session()
        stmt = (
            select(StateTable)
            .filter_by(name=state_name)
            .options(joinedload(StateTable.latest_version))
        )
        state = (await session.scalars(stmt)).first()
        if state is None:
            return State(
                id=ObjectID(None),
                name=state_name,
                latest_version=None,
            )

        return State(
            id=ObjectID(state.id),
            name=state.name,
            latest_version=None if state.latest_version is None else StateVersion(
                id=ObjectID(state.latest_version.id),
                version=state.latest_version.version,
                hash=state.latest_version.hash,
                path=state.latest_version.path,
            ),
        )

    async def save(self, state: State):
        db_session = await self._get_session()

        if state.id.is_new:
            state_table = StateTable(id=state.id.value, name=state.name)
            db_session.add(state_table)
        else:
            state_table = db_session.get(StateTable, state.id.value)

        if state.latest_version is not None:
            if state.latest_version.id.is_new:
                latest_version_table = StateVersionTable(
                    id=state.latest_version.id.value,
                    state_id=state.id.value,
                    version=state.latest_version.version,
                    hash=state.latest_version.hash,
                    path=state.latest_version.path,
                )
                db_session.add(latest_version_table)

        state_table.latest_version_id = state.latest_version.id.value if state.latest_version is not None else None

        await db_session.flush()
