"""Remove Members table and associations on other models

Revision ID: edeef2fc4b19
Revises: 2181bc7f91a7
Create Date: 2025-07-21 15:16:37.299240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'edeef2fc4b19'
down_revision: Union[str, Sequence[str], None] = '2181bc7f91a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_members_id'), table_name='members')
    op.drop_table('members')
    op.drop_index(op.f('ix_toons_member_id'), table_name='toons')
    op.drop_constraint(op.f('uq_toon_member_username'), 'toons', type_='unique')
    op.drop_constraint(op.f('toons_member_id_fkey'), 'toons', type_='foreignkey')
    op.drop_column('toons', 'member_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('toons', sa.Column('member_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key(op.f('toons_member_id_fkey'), 'toons', 'members', ['member_id'], ['id'])
    op.create_unique_constraint(op.f('uq_toon_member_username'), 'toons', ['member_id', 'username'], postgresql_nulls_not_distinct=False)
    op.create_index(op.f('ix_toons_member_id'), 'toons', ['member_id'], unique=False)
    op.create_table('members',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('guild_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('display_name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('rank', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('join_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.CheckConstraint("display_name::text <> ''::text", name=op.f('ck_member_display_name_not_empty')),
    sa.ForeignKeyConstraint(['guild_id'], ['guilds.id'], name=op.f('members_guild_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('members_pkey')),
    sa.UniqueConstraint('guild_id', 'display_name', name=op.f('uq_member_guild_display_name'), postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index(op.f('ix_members_id'), 'members', ['id'], unique=False)
    # ### end Alembic commands ###
