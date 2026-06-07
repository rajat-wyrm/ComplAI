"""add users and roles

Revision ID: 001
Revises: 
Create Date: 2026-06-07
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.execute("CREATE TYPE userrole AS ENUM ('super_admin', 'admin', 'analyst', 'viewer')")
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('role', sa.Enum('super_admin', 'admin', 'analyst', 'viewer', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.add_column('documents', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_documents_user_id', 'documents', 'users', ['user_id'], ['id'])

def downgrade():
    op.drop_constraint('fk_documents_user_id', 'documents', type_='foreignkey')
    op.drop_column('documents', 'user_id')
    op.drop_table('users')
    op.execute("DROP TYPE userrole")
