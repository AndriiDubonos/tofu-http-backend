"""empty message

Revision ID: e063a1c75b52
Revises: 0591bf8a44e4
Create Date: 2025-05-08 15:23:55.193914

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e063a1c75b52"
down_revision: Union[str, None] = "0591bf8a44e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("states_state", sa.Column("lock_id", sa.UUID(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("states_state", "lock_id")
    # ### end Alembic commands ###
