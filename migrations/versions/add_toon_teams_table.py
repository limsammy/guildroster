"""Add toon_teams junction table

Revision ID: add_toon_teams_table
Revises: 64716582e5c9
Create Date: 2025-07-16 22:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_toon_teams_table"
down_revision: Union[str, Sequence[str], None] = "64716582e5c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create toon_teams junction table
    op.create_table(
        "toon_teams",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("toon_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["toon_id"],
            ["toons.id"],
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("toon_id", "team_id", name="uq_toon_team_unique"),
    )
    op.create_index(
        op.f("ix_toon_teams_id"), "toon_teams", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_toon_teams_toon_id"), "toon_teams", ["toon_id"], unique=False
    )
    op.create_index(
        op.f("ix_toon_teams_team_id"), "toon_teams", ["team_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_toon_teams_team_id"), table_name="toon_teams")
    op.drop_index(op.f("ix_toon_teams_toon_id"), table_name="toon_teams")
    op.drop_index(op.f("ix_toon_teams_id"), table_name="toon_teams")
    op.drop_table("toon_teams")
