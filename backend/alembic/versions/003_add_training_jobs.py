"""add training_jobs table

Revision ID: 003
Revises: 001
Create Date: 2025-11-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '003'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'training_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        
        # Configuration
        sa.Column('model_name', sa.String(), nullable=False),
        sa.Column('epochs', sa.Integer(), nullable=False),
        sa.Column('batch_size', sa.Integer(), nullable=False),
        sa.Column('img_size', sa.Integer(), nullable=False),
        sa.Column('learning_rate', sa.Float(), nullable=False),
        sa.Column('patience', sa.Integer(), nullable=False),
        sa.Column('config', postgresql.JSONB()),
        
        # Status
        sa.Column('status', sa.String(), server_default='pending'),
        sa.Column('progress', sa.Float(), server_default='0.0'),
        sa.Column('current_epoch', sa.Integer(), server_default='0'),
        
        # Metrics
        sa.Column('metrics', postgresql.JSONB()),
        
        # Paths
        sa.Column('dataset_path', sa.String()),
        sa.Column('model_path', sa.String()),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        
        # Error
        sa.Column('error_message', sa.String())
    )
    
    # Create indexes
    op.create_index('idx_training_jobs_project_id', 'training_jobs', ['project_id'])
    op.create_index('idx_training_jobs_status', 'training_jobs', ['status'])
    op.create_index('idx_training_jobs_created_at', 'training_jobs', ['created_at'])


def downgrade():
    op.drop_table('training_jobs')
