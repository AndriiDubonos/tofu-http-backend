import uuid

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Integer

from apps.common.sqlalchemy.defaults import server_default_uuid4, server_default_now
from tofu_http_backend.sqlalchemy import Base


class StateVersion(Base):
    __tablename__ = 'states_state_version'
    # Looks like terraform can send the same state multiple times
    # __table_args__ = (
    #     UniqueConstraint('state_id', 'version', name='states_state_version_unique_state_version_index'),
    # )

    id = Column(
        UUID(as_uuid=True), primary_key=True, unique=True,
        default=uuid.uuid4, server_default=server_default_uuid4,
    )
    created_date = Column(DateTime(timezone=True), nullable=False, server_default=server_default_now)
    modified_date = Column(DateTime(timezone=True), nullable=False, server_default=server_default_now)

    state_id = Column(UUID(as_uuid=True), ForeignKey('states_state.id'), index=True)
    version = Column(Integer(), nullable=False)

    hash = Column(String(length=256), nullable=False)
    path = Column(String(length=256), nullable=False)
