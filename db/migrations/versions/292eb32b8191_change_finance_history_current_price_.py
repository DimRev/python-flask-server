"""change finance_history.current_price from int to float

Revision ID: 292eb32b8191
Revises: 60dbf26bceeb
Create Date: 2024-12-21 23:04:24.636270

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "292eb32b8191"
down_revision: Union[str, None] = "60dbf26bceeb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Create a new table with the modified column type
    op.create_table(
        "finance_history_new",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "finance_id",
            sa.Integer,
            sa.ForeignKey("finances.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("current_price", sa.Float, nullable=False),  # Changed to Float
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            nullable=False,
            default=sa.func.current_timestamp,
        ),
    )

    # Step 2: Copy data from the old table to the new table
    op.execute(
        """
        INSERT INTO finance_history_new (id, finance_id, current_price, created_at)
        SELECT id, finance_id, current_price, created_at
        FROM finance_history
    """
    )

    # Step 3: Drop the old table
    op.drop_table("finance_history")

    # Step 4: Rename the new table to the old table's name
    op.rename_table("finance_history_new", "finance_history")


def downgrade() -> None:
    # Step 1: Create the old table with the original schema
    op.create_table(
        "finance_history_old",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "finance_id",
            sa.Integer,
            sa.ForeignKey("finances.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("current_price", sa.Integer, nullable=False),  # Reverted to Integer
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            nullable=False,
            default=sa.func.current_timestamp,
        ),
    )

    # Step 2: Copy data back from the current table to the old table
    op.execute(
        """
        INSERT INTO finance_history_old (id, finance_id, current_price, created_at)
        SELECT id, finance_id, current_price, created_at
        FROM finance_history
    """
    )

    # Step 3: Drop the current table
    op.drop_table("finance_history")

    # Step 4: Rename the old table to the current table's name
    op.rename_table("finance_history_old", "finance_history")
