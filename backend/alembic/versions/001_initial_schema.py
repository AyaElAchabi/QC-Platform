"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-01-01 00:00:00.000000

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
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    
    # Users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('email_verified', sa.Boolean(), default=False),
        sa.Column('last_login', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'))
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role', 'users', ['role'])
    
    # Products table
    op.create_table('products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'))
    )
    op.create_index('idx_products_type', 'products', ['type'])
    op.create_index('idx_products_name', 'products', ['name'])
    
    # Classes table
    op.create_table('classes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('color_hex', sa.String(7), default='#FF5733'),
        sa.Column('description', sa.Text()),
        sa.Column('severity', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('product_id', 'name')
    )
    op.create_index('idx_classes_product_id', 'classes', ['product_id'])
    op.create_index('idx_classes_name', 'classes', ['name'])
    
    # Projects table
    op.create_table('projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='SET NULL')),
        sa.Column('task_type', sa.String(50)),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'))
    )
    op.create_index('idx_projects_owner_id', 'projects', ['owner_id'])
    op.create_index('idx_projects_product_id', 'projects', ['product_id'])
    op.create_index('idx_projects_status', 'projects', ['status'])
    
    # Project members table
    op.create_table('project_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('role', sa.String(50)),
        sa.Column('added_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('project_id', 'user_id')
    )
    op.create_index('idx_project_members_project_id', 'project_members', ['project_id'])
    op.create_index('idx_project_members_user_id', 'project_members', ['user_id'])
    
    # Images table
    op.create_table('images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('storage_path', sa.String(512), nullable=False),
        sa.Column('thumbnail_path', sa.String(512)),
        sa.Column('file_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('file_size_bytes', sa.Integer()),
        sa.Column('format', sa.String(10)),
        sa.Column('exif_metadata', postgresql.JSONB()),
        sa.Column('status', sa.String(50), default='uploaded'),
        sa.Column('split', sa.String(10)),
        sa.Column('annotation_count', sa.Integer(), default=0),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.CheckConstraint('width >= 100'),
        sa.CheckConstraint('height >= 100')
    )
    op.create_index('idx_images_project_id', 'images', ['project_id'])
    op.create_index('idx_images_status', 'images', ['status'])
    op.create_index('idx_images_split', 'images', ['split'])
    op.create_index('idx_images_file_hash', 'images', ['file_hash'])
    op.create_index('idx_images_created_at', 'images', ['created_at'])
    
    # Annotations table
    op.create_table('annotations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('image_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('images.id', ondelete='CASCADE'), nullable=False),
        sa.Column('class_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('bbox', postgresql.JSONB(), nullable=False),
        sa.Column('mask', postgresql.JSONB()),
        sa.Column('confidence', sa.Float()),
        sa.Column('source', sa.String(50), default='manual'),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'))
    )
    op.create_index('idx_annotations_image_id', 'annotations', ['image_id'])
    op.create_index('idx_annotations_class_id', 'annotations', ['class_id'])
    op.create_index('idx_annotations_source', 'annotations', ['source'])


def downgrade() -> None:
    op.drop_table('annotations')
    op.drop_table('images')
    op.drop_table('project_members')
    op.drop_table('projects')
    op.drop_table('classes')
    op.drop_table('products')
    op.drop_table('users')