"""add_authoritative_metadata

Revision ID: c1f930e49d82
Revises: bd4a83b26495
Create Date: 2026-10-11 12:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1f930e49d82'
down_revision: Union[str, None] = 'bd4a83b26495'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('knowledge_sources', sa.Column('provenance_file', sa.String(length=512), nullable=True))
    op.add_column('knowledge_sources', sa.Column('publish_date', sa.String(length=50), nullable=True))
    op.add_column('knowledge_sources', sa.Column('episode_duration', sa.String(length=50), nullable=True))
    op.add_column('knowledge_sources', sa.Column('is_authoritative', sa.Boolean(), server_default='1', nullable=False))


def downgrade() -> None:
    op.drop_column('knowledge_sources', 'is_authoritative')
    op.drop_column('knowledge_sources', 'episode_duration')
    op.drop_column('knowledge_sources', 'publish_date')
    op.drop_column('knowledge_sources', 'provenance_file')
