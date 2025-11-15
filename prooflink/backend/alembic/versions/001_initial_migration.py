"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('subscription_tier', sa.String(50), default='free', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    )

    # Create proofs table
    op.create_table(
        'proofs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=False, index=True),
        sa.Column('file_name', sa.String(255), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('proof_link', sa.String(500), nullable=False, unique=True, index=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    )

    # Create proof_verifications table
    op.create_table(
        'proof_verifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('proof_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('proofs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('result', sa.Boolean(), nullable=False),
    )

    # Create indexes
    op.create_index('idx_proofs_created_at', 'proofs', ['created_at'])
    op.create_index('idx_verifications_verified_at', 'proof_verifications', ['verified_at'])


def downgrade() -> None:
    op.drop_index('idx_verifications_verified_at')
    op.drop_index('idx_proofs_created_at')
    op.drop_table('proof_verifications')
    op.drop_table('proofs')
    op.drop_table('users')