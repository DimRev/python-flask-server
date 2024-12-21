"""create finance tables

Revision ID: 60dbf26bceeb
Revises: def5faf454e6
Create Date: 2024-12-21 09:16:59.300967

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "60dbf26bceeb"
down_revision: Union[str, None] = "def5faf454e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the 'finances' table
    op.create_table(
        "finances",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("symbol", sa.String(50), nullable=False, unique=True),
        sa.Column("is_tracking", sa.Boolean, nullable=False, default=False),
        sa.Column("last_closing_price", sa.Integer, nullable=True),
        sa.Column("daily_change_value", sa.Float, nullable=True),
        sa.Column("daily_change_percentage", sa.Float, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            nullable=False,
            default=sa.func.current_timestamp,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP,
            nullable=False,
            default=sa.func.current_timestamp,
            onupdate=sa.func.current_timestamp,
        ),
    )

    # Create the 'finance_history' table
    op.create_table(
        "finance_history",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "finance_id",
            sa.Integer,
            sa.ForeignKey("finances.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("current_price", sa.Integer, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            nullable=False,
            default=sa.func.current_timestamp,
        ),
    )


def downgrade() -> None:
    # Drop the 'finance_history' table
    op.drop_table("finance_history")

    # Drop the 'finances' table
    op.drop_table("finances")
