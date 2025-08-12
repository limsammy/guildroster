"""update_toon_role_constraint_to_include_melee_and_ranged_dps

Revision ID: a141e95f48b1
Revises: f010aacf9088
Create Date: 2025-08-11 19:24:55.955533

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a141e95f48b1"
down_revision: Union[str, Sequence[str], None] = "f010aacf9088"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the old constraint
    op.drop_constraint("ck_toon_role_valid", "toons", type_="check")

    # Add the new constraint with updated role values
    op.create_check_constraint(
        "ck_toon_role_valid",
        "toons",
        "role IN ('Melee DPS', 'Ranged DPS', 'Healer', 'Tank')",
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the new constraint
    op.drop_constraint("ck_toon_role_valid", "toons", type_="check")

    # Add back the old constraint
    op.create_check_constraint(
        "ck_toon_role_valid", "toons", "role IN ('DPS', 'Healer', 'Tank')"
    )
