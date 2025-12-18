"""make_is_removed_non_nullable

Revision ID: 82fd2d7e1982
Revises: 379cb7e85eaf
Create Date: 2025-12-18 10:18:40.813235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82fd2d7e1982'
down_revision: Union[str, Sequence[str], None] = '379cb7e85eaf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Update existing NULL values to False
    op.execute("UPDATE order_items SET is_removed = false WHERE is_removed IS NULL")
    
    # 2. Alter column to be NOT NULL with default False
    op.alter_column('order_items', 'is_removed',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               server_default=sa.text('false'))


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('order_items', 'is_removed',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               server_default=None)
