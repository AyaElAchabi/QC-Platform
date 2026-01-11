"""Add models table

Revision ID: 004_add_models_table
Revises: 003_add_training_jobs
Create Date: 2025-11-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'models',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('training_job_id', UUID(as_uuid=True), sa.ForeignKey('training_jobs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('task_type', sa.String(50), nullable=False),
        sa.Column('architecture', sa.String(100), nullable=False),
        sa.Column('storage_path', sa.String(512), nullable=False),
        sa.Column('mlflow_model_uri', sa.String(512)),
        sa.Column('metrics', JSONB, nullable=False),
        sa.Column('hyperparameters', JSONB),
        sa.Column('stage', sa.String(50), default='staging', index=True),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('inference_count', sa.Integer, default=0),
        sa.Column('avg_inference_time_ms', sa.Float),
        sa.Column('model_card_path', sa.String(512)),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('promoted_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('promoted_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('models')
