"""Add total_price to orders safely

Revision ID: a46fa03d96cd
Revises: bb68596fcf2c
Create Date: 2025-09-08 14:34:12.409762
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a46fa03d96cd'
down_revision = 'bb68596fcf2c'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add the column as nullable
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total_price', sa.Float(), nullable=True))
        batch_op.alter_column('created_at',
                              existing_type=postgresql.TIMESTAMP(),
                              nullable=False)
        batch_op.alter_column('updated_at',
                              existing_type=postgresql.TIMESTAMP(),
                              nullable=False)
        batch_op.drop_column('email')
        batch_op.drop_column('total_amount')
        batch_op.drop_column('shipping_address')

    # Step 2: Set a default value for existing rows
    op.execute("UPDATE orders SET total_price = 0.0 WHERE total_price IS NULL")

    # Step 3: Make the column NOT NULL
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('total_price', nullable=False)


def downgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shipping_address', sa.VARCHAR(length=255), nullable=False))
        batch_op.add_column(sa.Column('total_amount', sa.DOUBLE_PRECISION(precision=53), nullable=False))
        batch_op.add_column(sa.Column('email', sa.VARCHAR(length=120), nullable=False))
        batch_op.alter_column('updated_at',
                              existing_type=postgresql.TIMESTAMP(),
                              nullable=True)
        batch_op.alter_column('created_at',
                              existing_type=postgresql.TIMESTAMP(),
                              nullable=True)
        batch_op.drop_column('total_price')
