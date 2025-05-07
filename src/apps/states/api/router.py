from fastapi import APIRouter, Request
from fastapi.exceptions import ValidationException, HTTPException

from apps.common.unit_of_work.default import get_default_unit_of_work

router = APIRouter(prefix='states/{state_name}')


@router.get('')
async def get_latest_state(state_name: str, request: Request) -> dict[str, str]:  # TODO: constraint string
    print(await request.body())
    raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "success"}


@router.post('')
async def update_state(state_name: str, request: Request) -> dict[str, str]:  # TODO: constraint string
    print(await request.body())

    return {"status": "success"}


@router.delete('')
async def purge_state(state_name: str, request: Request) -> dict[str, str]:  # TODO: constraint string
    print(await request.body())

    return {"status": "success"}


@router.post('/lock')
async def lock_state(state_name: str, request: Request) -> dict[str, str]:  # TODO: constraint string
    print(await request.body())

    return {"status": "success"}


@router.post('/unlock')
async def unlock_state(state_name: str, request: Request) -> dict[str, str]:  # TODO: constraint string
    print(await request.body())
    # use_case = CreateUserUseCase(error_class=ValidationException)
    # async with get_default_unit_of_work() as unit_of_work:
    #     await use_case.execute(unit_of_work=unit_of_work, raw_data=user)

    return {"status": "success"}
