import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.states.use_cases.states.update_state import UpdateStateUseCase
from tests.setupers.unit_of_work import get_active_unit_of_work


async def _execute(active_transaction_session: AsyncSession):
    async with get_active_unit_of_work(active_db_session=active_transaction_session) as uow:
        UpdateStateUseCase(unit_of_work=uow, error_class=Exception)


@pytest.mark.asyncio
async def test_update_state(
        active_transaction_session: AsyncSession,
):
    await _execute(active_transaction_session=active_transaction_session)
