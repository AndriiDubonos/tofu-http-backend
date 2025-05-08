from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Request, Body, Query
from fastapi.exceptions import ValidationException, HTTPException

from apps.common.unit_of_work.default import get_default_unit_of_work
from apps.states.use_cases.states.get_latest_state import GetLatestStateUseCase
from apps.states.use_cases.states.lock_state import LockStateUseCase
from apps.states.use_cases.states.unlock_state import UnlockStateUseCase
from apps.states.use_cases.states.update_state import UpdateStateUseCase

router = APIRouter(prefix='/states/{state_name}')


@router.get('')
async def get_latest_state(state_name: str, request: Request) -> bytes:  # TODO: constraint string
    async with get_default_unit_of_work(app=request.app) as unit_of_work:
        use_case = GetLatestStateUseCase(unit_of_work=unit_of_work, error_class=ValidationException)
        latest_state = await use_case.execute(state_name=state_name)

    if latest_state is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return latest_state


@router.post('')
async def update_state(state_name: str, lock_id: Annotated[UUID, Query(alias='ID')], request: Request) -> dict[str, str]:  # TODO: constraint string
    async with get_default_unit_of_work(app=request.app) as unit_of_work:
        use_case = UpdateStateUseCase(unit_of_work=unit_of_work, error_class=ValidationException)
        await use_case.execute(state_name=state_name, raw_state_data=await request.body(), lock_id=lock_id)

    return {"status": "success"}


@router.post('/lock')
async def lock_state(state_name: str, lock_id: Annotated[UUID, Body(alias='ID', embed=True)], request: Request) -> dict[str, str]:  # TODO: constraint string
    async with get_default_unit_of_work(app=request.app) as unit_of_work:
        use_case = LockStateUseCase(unit_of_work=unit_of_work, error_class=ValidationException)
        await use_case.execute(state_name=state_name, lock_id=lock_id)
    return {"status": "success"}


@router.post('/unlock')
async def unlock_state(state_name: str, lock_id: Annotated[UUID, Body(alias='ID', embed=True)], request: Request) -> dict[str, str]:  # TODO: constraint string
    async with get_default_unit_of_work(app=request.app) as unit_of_work:
        use_case = UnlockStateUseCase(unit_of_work=unit_of_work, error_class=ValidationException)
        await use_case.execute(state_name=state_name, lock_id=lock_id, force=False)

    return {"status": "success"}
