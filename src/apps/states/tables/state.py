import uuid

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID

from apps.common.sqlalchemy.defaults import server_default_uuid4, server_default_now
from tofu_http_backend.sqlalchemy import Base


class State(Base):
    __tablename__ = "states_state"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        server_default=server_default_uuid4,
    )
    created_date = Column(
        DateTime(timezone=True), nullable=False, server_default=server_default_now
    )
    modified_date = Column(
        DateTime(timezone=True), nullable=False, server_default=server_default_now
    )

    name = Column(String(length=64), nullable=False, unique=True)
    latest_version = Column(
        UUID(as_uuid=True), ForeignKey("states_state_version.id"), nullable=True
    )
    lock_id = Column(UUID(as_uuid=True), nullable=True)
