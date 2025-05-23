from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Request, Body, Query, Depends
from fastapi.exceptions import HTTPException
from starlette.responses import Response

from apps.common.unit_of_work.default import get_default_unit_of_work
from apps.states.api.dependencies import state_name_extractor, get_current_username
from apps.states.domain.states.errors import BaseStateError, ConcurrentLockError
from apps.states.use_cases.states.get_latest_state import GetLatestStateUseCase
from apps.states.use_cases.states.lock_state import LockStateUseCase
from apps.states.use_cases.states.unlock_state import UnlockStateUseCase
from apps.states.use_cases.states.update_state import UpdateStateUseCase

router = APIRouter(
    prefix="/states/{state_name}",
    dependencies=[Depends(get_current_username)],
)


@router.get("")
async def get_latest_state(
    state_name: Annotated[str, Depends(state_name_extractor)], request: Request
) -> Response:
    async with get_default_unit_of_work(app=request.app) as unit_of_work:
        use_case = GetLatestStateUseCase(unit_of_work=unit_of_work)
        latest_state = await use_case.execute(state_name=state_name)

    if latest_state is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return Response(latest_state)


@router.post("")
async def update_state(
    state_name: Annotated[str, Depends(state_name_extractor)],
    lock_id: Annotated[UUID, Query(alias="ID")],
    request: Request,
) -> dict[str, str]:
    async with get_default_unit_of_work(app=request.app) as unit_of_work:
        use_case = UpdateStateUseCase(unit_of_work=unit_of_work)
        try:
            await use_case.execute(
                state_name=state_name,
                raw_state_data=await request.body(),
                lock_id=lock_id,
            )
        except BaseStateError as e:
            raise HTTPException(status_code=404, detail=e.message)

    return {"status": "success"}


@router.post("/lock")
async def lock_state(
    state_name: Annotated[str, Depends(state_name_extractor)],
    lock_id: Annotated[UUID, Body(alias="ID", embed=True)],
    request: Request,
) -> dict[str, str]:
    async with get_default_unit_of_work(app=request.app) as unit_of_work:
        use_case = LockStateUseCase(unit_of_work=unit_of_work)
        try:
            await use_case.execute(state_name=state_name, lock_id=lock_id)
        except ConcurrentLockError as e:
            raise HTTPException(status_code=409, detail=e.message)

    return {"status": "success"}


@router.post("/unlock")
async def unlock_state(
    state_name: Annotated[str, Depends(state_name_extractor)],
    lock_id: Annotated[UUID, Body(alias="ID", embed=True)],
    request: Request,
) -> dict[str, str]:
    async with get_default_unit_of_work(app=request.app) as unit_of_work:
        use_case = UnlockStateUseCase(unit_of_work=unit_of_work)
        try:
            await use_case.execute(state_name=state_name, lock_id=lock_id, force=False)
        except ConcurrentLockError as e:
            raise HTTPException(status_code=409, detail=e.message)

    return {"status": "success"}
