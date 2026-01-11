"""
Update user role to ENUM and add role-based permissions

Revision ID: 006_add_role_enum
Revises: 005_add_predictions_table
Create Date: 2025-12-15 16:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Créer l'ENUM des rôles
    role_enum = postgresql.ENUM(
        'ADMIN', 
        'CHEF_OPERATOR', 
        'OPERATOR', 
        'VIEWER',
        name='userrole',
        create_type=True
    )
    role_enum.create(op.get_bind(), checkfirst=True)
    
    # Mettre à jour les valeurs existantes pour correspondre aux nouveaux enums
    op.execute("""
        UPDATE users 
        SET role = CASE 
            WHEN role = 'admin' THEN 'ADMIN'
            WHEN role = 'chef_operator' THEN 'CHEF_OPERATOR'
            WHEN role = 'operator' THEN 'OPERATOR'
            ELSE 'OPERATOR'  -- Par défaut, ancien 'viewer' devient OPERATOR
        END
    """)
    
    # Changer le type de la colonne
    op.alter_column(
        'users', 
        'role',
        type_=role_enum,
        existing_type=sa.String(),
        postgresql_using='role::userrole',
        nullable=False
    )
    
    # Changer la valeur par défaut
    op.alter_column(
        'users',
        'role',
        server_default='OPERATOR'
    )


def downgrade() -> None:
    # Revenir à String
    op.alter_column(
        'users', 
        'role',
        type_=sa.String(),
        existing_type=postgresql.ENUM('ADMIN', 'CHEF_OPERATOR', 'OPERATOR', 'VIEWER', name='userrole'),
        nullable=False
    )
    
    # Supprimer l'ENUM
    role_enum = postgresql.ENUM(
        'ADMIN', 
        'CHEF_OPERATOR', 
        'OPERATOR', 
        'VIEWER',
        name='userrole'
    )
    role_enum.drop(op.get_bind(), checkfirst=True)
    
    # Revenir aux anciennes valeurs
    op.execute("""
        UPDATE users 
        SET role = CASE 
            WHEN role = 'ADMIN' THEN 'admin'
            WHEN role = 'CHEF_OPERATOR' THEN 'chef_operator'
            WHEN role = 'OPERATOR' THEN 'operator'
            WHEN role = 'VIEWER' THEN 'viewer'
            ELSE 'viewer'
        END
    """)
