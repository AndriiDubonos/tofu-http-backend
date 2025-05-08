from domain_model.object_id import ObjectID
from pydantic import BaseModel


class StateVersion(BaseModel):
    id: ObjectID

    version: int

    hash: str
    path: str


class State(BaseModel):
    id: ObjectID
    name: str
    latest_version: StateVersion | None
