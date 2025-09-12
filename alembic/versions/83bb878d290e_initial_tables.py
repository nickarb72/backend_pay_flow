"""initial_tables

Revision ID: 83bb878d290e
Revises: 
Create Date: 2025-09-10 15:52:12.362472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '83bb878d290e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("BEGIN")
    try:
        op.create_table('users',
                        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
                        sa.Column('email', sa.String(length=255), nullable=False),
                        sa.Column('hashed_password', sa.String(length=255), nullable=False),
                        sa.Column('full_name', sa.String(length=100), nullable=True),
                        sa.Column('role', sa.Enum('USER', 'ADMIN', name='userrole'), nullable=False),
                        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
                        sa.Column('updated_at', sa.DateTime(timezone=True)),
                        sa.PrimaryKeyConstraint('id')
                        )
        op.create_index('ix_users_email', 'users', ['email'], unique=True)
        op.create_index('ix_users_id', 'users', ['id'], unique=False)

        op.create_table('accounts',
                        sa.Column('id', sa.BigInteger(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=False),
                        sa.Column('balance', sa.Numeric(scale=2), server_default='0.00', nullable=False),
                        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
                        sa.Column('updated_at', sa.DateTime(timezone=True)),
                        sa.PrimaryKeyConstraint('id'),
                        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
                        )
        op.create_index('ix_accounts_id', 'accounts', ['id'], unique=False)
        op.create_index('ix_accounts_user_id', 'accounts', ['user_id'], unique=False)

        op.create_table('payments',
                        sa.Column('transaction_id', postgresql.UUID(), nullable=False),
                        sa.Column('user_id', sa.BigInteger(), nullable=True),
                        sa.Column('account_id', sa.BigInteger(), nullable=True),
                        sa.Column('amount', sa.Numeric(scale=2), nullable=False),
                        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
                        sa.PrimaryKeyConstraint('transaction_id'),
                        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
                        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='SET NULL')
                        )
        op.create_index('ix_payments_transaction_id', 'payments', ['transaction_id'], unique=False)
        op.execute("COMMIT")
    except:
        op.execute("ROLLBACK")
        raise


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('payments')
    op.drop_table('accounts')
    op.drop_table('users')

    op.execute("DROP TYPE userrole")
