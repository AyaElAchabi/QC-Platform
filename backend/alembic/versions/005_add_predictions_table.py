"""Add predictions table

Revision ID: 005
Revises: 004
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'predictions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('model_id', UUID(as_uuid=True), sa.ForeignKey('models.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('image_path', sa.String(512), nullable=True),
        sa.Column('results', JSONB, nullable=False),
        sa.Column('inference_time_ms', sa.Float, nullable=False),
        sa.Column('confidence_threshold', sa.Float, default=0.25),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
    )
    
    # Index pour recherches rapides
    op.create_index('ix_predictions_created_at', 'predictions', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_predictions_created_at')
    op.drop_table('predictions')
