"""add_test_data

Revision ID: d8de9eb27d89
Revises: 83bb878d290e
Create Date: 2025-09-10 16:42:59.535387

"""
from datetime import datetime, timezone
from typing import Sequence, Union

from _decimal import Decimal
from alembic import op
from sqlalchemy import func
import sqlalchemy as sa

from app.core.security import get_password_hash

# revision identifiers, used by Alembic.
revision: str = 'd8de9eb27d89'
down_revision: Union[str, Sequence[str], None] = '83bb878d290e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    users_table = sa.table('users',
                           sa.column('id', sa.BigInteger()),
                           sa.column('email', sa.String()),
                           sa.column('hashed_password', sa.String()),
                           sa.column('full_name', sa.String()),
                           sa.column('role', sa.Enum('USER', 'ADMIN', name='userrole')),
                           sa.column('created_at', sa.DateTime()),
                           sa.column('updated_at', sa.DateTime()),
                           )
    
    current_time = datetime.now()
    
    op.bulk_insert(users_table, [
        {
            'email': 'test_user@example.com',
            'hashed_password': get_password_hash('test_user_password'),
            'full_name': 'Test User',
            'role': 'USER',
            'created_at': current_time,
            'updated_at': None
        },
        {
            'email': 'test_admin@example.com',
            'hashed_password': get_password_hash('test_admin_password'),
            'full_name': 'Test Admin',
            'role': 'ADMIN',
            'created_at': current_time,
            'updated_at': None
        }
    ])

    accounts_table = sa.table('accounts',
                              sa.column('id', sa.BigInteger()),
                              sa.column('user_id', sa.BigInteger()),
                              sa.column('balance', sa.Numeric()),
                              sa.column('created_at', sa.DateTime()),
                              sa.column('updated_at', sa.DateTime()),
                              )

    op.bulk_insert(accounts_table, [
        {
            'id': 1,
            'user_id': 1,
            'balance': Decimal('0.00'),
            'created_at': current_time,
            'updated_at': None
        }
    ])


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM accounts WHERE id = 1")
    op.execute("DELETE FROM users WHERE id IN (1, 2)")
