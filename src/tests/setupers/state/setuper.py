from uuid import UUID, uuid4

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.states.tables.state import State as StateTable
from apps.states.tables.state_version import StateVersion as StateVersionTable


class StateSetuper:
    """Setuper for creating and managing states in tests."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create_state(self, state_name: str) -> UUID:
        # Check if state already exists
        stmt = select(StateTable).filter_by(name=state_name)
        existing_state = (await self._session.scalars(stmt)).first()
        
        if existing_state is not None:
            return existing_state.id
        
        # Create new state
        state_id = uuid4()
        stmt = insert(StateTable).values(
            id=state_id,
            name=state_name,
            latest_version=None,
            lock_id=None
        )
        await self._session.execute(stmt)
        await self._session.flush()
        
        return state_id
    
    async def lock_state(self, state_name: str, lock_id: UUID = None) -> UUID:
        state_id = await self.create_state(state_name)

        lock_id = lock_id or uuid4()

        stmt = update(StateTable).where(StateTable.id == state_id).values(lock_id=lock_id)
        await self._session.execute(stmt)
        await self._session.flush()
        
        return lock_id
    
    async def unlock_state(self, state_name: str) -> None:
        stmt = select(StateTable).filter_by(name=state_name)
        state = (await self._session.scalars(stmt)).first()
        
        if state is None:
            return
        
        stmt = update(StateTable).where(StateTable.id == state.id).values(lock_id=None)
        await self._session.execute(stmt)
        await self._session.flush()
    
    async def add_state_version(self, state_name: str, version: int, hash_value: str = None, path: str = None) -> UUID:
        # Ensure state exists
        state_id = await self.create_state(state_name)
        
        # Generate values if not provided
        version_id = uuid4()
        if hash_value is None:
            hash_value = f"hash_{uuid4().hex[:8]}"
        
        if path is None:
            path = f"{state_id}/versions/{version_id}.json"
        
        # Create version
        stmt = insert(StateVersionTable).values(
            id=version_id,
            state_id=state_id,
            version=version,
            hash=hash_value,
            path=path
        )
        await self._session.execute(stmt)
        
        # Update state to point to the new version
        stmt = update(StateTable).where(StateTable.id == state_id).values(latest_version=version_id)
        await self._session.execute(stmt)
        await self._session.flush()
        
        return version_id

    async def get_state(self, state_name: str) -> tuple[StateTable | None, StateVersionTable | None]:
        # Get state with join to version
        stmt = (
            select(StateTable, StateVersionTable)
            .filter(StateTable.name == state_name)
            .outerjoin(StateVersionTable, StateTable.latest_version == StateVersionTable.id)
        )
        result = (await self._session.execute(stmt)).first()

        if result is None:
            return None, None

        state, state_version = result
        return state, state_version

    def generate_raw_state_data(self, version: int = 1) -> bytes:
        """Generate raw state data for testing"""
        raw_data = b'{"version":<version>,"terraform_version":"1.9.1","serial":1,"lineage":"2fbf9278-4e7b-1228-9f69-d27ce621d75b","outputs":{},"resources":[{"mode":"managed","type":"null_resource","name":"example","provider":"provider[\\"registry.opentofu.org/hashicorp/null\\"]","instances":[{"schema_version":0,"attributes":{"id":"588398148598976215","triggers":{"always_run":"2025-05-07T16:24:13Z"}},"sensitive_attributes":[]}]}],"check_results":null}\n'
        return raw_data.replace(b'<version>', f'{version}'.encode('utf8'))
