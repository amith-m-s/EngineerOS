"""Initial schema creation with users, twins, and memories.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-06-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema."""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('roles', sa.String(255), server_default='engineer'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_is_active', 'users', ['is_active'])

    # Create engineer_twins table
    op.create_table(
        'engineer_twins',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('user_id', sa.String(255), sa.ForeignKey('users.id'), nullable=False, unique=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('skill_scores_json', sa.Text()),
        sa.Column('debugging_score', sa.Integer(), server_default='0'),
        sa.Column('architecture_score', sa.Integer(), server_default='0'),
        sa.Column('reliability_score', sa.Integer(), server_default='0'),
        sa.Column('leadership_score', sa.Integer(), server_default='0'),
        sa.Column('system_design_score', sa.Integer(), server_default='0'),
        sa.Column('memory_count', sa.Integer(), server_default='0'),
        sa.Column('graph_nodes', sa.Integer(), server_default='0'),
        sa.Column('vector_embeddings', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_engineer_twins_user_id', 'engineer_twins', ['user_id'])

    # Create engineer_memories table
    op.create_table(
        'engineer_memories',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('user_id', sa.String(255), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('twin_id', sa.String(255), sa.ForeignKey('engineer_twins.id'), nullable=False),
        sa.Column('kind', sa.String(50), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('signal_strength', sa.Integer(), server_default='50'),
        sa.Column('details_json', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_engineer_memories_user_id', 'engineer_memories', ['user_id'])
    op.create_index('ix_engineer_memories_kind', 'engineer_memories', ['kind'])

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('user_id', sa.String(255), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(255), nullable=False),
        sa.Column('resource', sa.String(255), nullable=False),
        sa.Column('resource_id', sa.String(255), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('details_json', sa.Text()),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(512)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('audit_logs')
    op.drop_table('engineer_memories')
    op.drop_table('engineer_twins')
    op.drop_table('users')
