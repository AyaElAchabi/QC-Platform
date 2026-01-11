"""
User roles and permissions enums
"""
from enum import Enum
from typing import List, Set


class UserRole(str, Enum):
    """
    Hiérarchie des rôles utilisateurs
    """
    ADMIN = "ADMIN"  # Admin/Account Owner - Tous les droits
    CHEF_OPERATOR = "CHEF_OPERATOR"  # Chef Operator - Gestion équipe + training
    OPERATOR = "OPERATOR"  # Operator - Annotation + inférence basique
    VIEWER = "VIEWER"  # Viewer - Lecture seule (legacy)


class Permission(str, Enum):
    """
    Permissions granulaires du système
    """
    # Gestion des utilisateurs
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_PROMOTE = "user:promote"  # Changer les rôles
    
    # Gestion des projets
    PROJECT_READ = "project:read"
    PROJECT_CREATE = "project:create"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    
    # Gestion des images
    IMAGE_READ = "image:read"
    IMAGE_UPLOAD = "image:upload"
    IMAGE_DELETE = "image:delete"
    
    # Annotations
    ANNOTATION_READ = "annotation:read"
    ANNOTATION_CREATE = "annotation:create"
    ANNOTATION_UPDATE = "annotation:update"
    ANNOTATION_DELETE = "annotation:delete"
    ANNOTATION_VALIDATE = "annotation:validate"  # Valider les annotations des autres
    
    # Training de modèles
    TRAINING_READ = "training:read"
    TRAINING_START = "training:start"
    TRAINING_CANCEL = "training:cancel"
    TRAINING_DELETE = "training:delete"
    
    # Modèles
    MODEL_READ = "model:read"
    MODEL_DOWNLOAD = "model:download"
    MODEL_DEPLOY = "model:deploy"  # Mettre en production
    MODEL_DELETE = "model:delete"
    
    # Inférence
    INFERENCE_RUN = "inference:run"
    INFERENCE_READ = "inference:read"
    INFERENCE_DELETE = "inference:delete"
    
    # Analytics & Reports
    ANALYTICS_READ = "analytics:read"
    REPORTS_GENERATE = "reports:generate"
    
    # Settings & Configuration
    SETTINGS_READ = "settings:read"
    SETTINGS_UPDATE = "settings:update"


# Matrice des permissions par rôle
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.ADMIN: {
        # Tous les droits (Admin/Account Owner)
        *Permission.__members__.values()
    },
    
    UserRole.CHEF_OPERATOR: {
        # Gestion d'équipe limitée
        Permission.USER_READ,
        Permission.USER_UPDATE,  # Peut modifier info des operators
        
        # Gestion complète des projets
        Permission.PROJECT_READ,
        Permission.PROJECT_CREATE,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_DELETE,
        
        # Gestion complète des images
        Permission.IMAGE_READ,
        Permission.IMAGE_UPLOAD,
        Permission.IMAGE_DELETE,
        
        # Gestion complète des annotations
        Permission.ANNOTATION_READ,
        Permission.ANNOTATION_CREATE,
        Permission.ANNOTATION_UPDATE,
        Permission.ANNOTATION_DELETE,
        Permission.ANNOTATION_VALIDATE,
        
        # Gestion complète du training
        Permission.TRAINING_READ,
        Permission.TRAINING_START,
        Permission.TRAINING_CANCEL,
        Permission.TRAINING_DELETE,
        
        # Gestion des modèles
        Permission.MODEL_READ,
        Permission.MODEL_DOWNLOAD,
        Permission.MODEL_DEPLOY,
        Permission.MODEL_DELETE,
        
        # Inférence complète
        Permission.INFERENCE_RUN,
        Permission.INFERENCE_READ,
        Permission.INFERENCE_DELETE,
        
        # Analytics
        Permission.ANALYTICS_READ,
        Permission.REPORTS_GENERATE,
        
        # Settings lecture seule
        Permission.SETTINGS_READ,
    },
    
    UserRole.OPERATOR: {
        # Lecture des utilisateurs
        Permission.USER_READ,
        
        # Projets (lecture + création limitée)
        Permission.PROJECT_READ,
        
        # Images (upload et lecture)
        Permission.IMAGE_READ,
        Permission.IMAGE_UPLOAD,
        
        # Annotations (CRUD de ses propres annotations)
        Permission.ANNOTATION_READ,
        Permission.ANNOTATION_CREATE,
        Permission.ANNOTATION_UPDATE,
        Permission.ANNOTATION_DELETE,
        
        # Training (lecture seule)
        Permission.TRAINING_READ,
        
        # Modèles (lecture + téléchargement)
        Permission.MODEL_READ,
        Permission.MODEL_DOWNLOAD,
        
        # Inférence (run + lecture)
        Permission.INFERENCE_RUN,
        Permission.INFERENCE_READ,
        
        # Analytics (lecture seule)
        Permission.ANALYTICS_READ,
    },
    
    UserRole.VIEWER: {
        # Lecture seule (legacy)
        Permission.USER_READ,
        Permission.PROJECT_READ,
        Permission.IMAGE_READ,
        Permission.ANNOTATION_READ,
        Permission.TRAINING_READ,
        Permission.MODEL_READ,
        Permission.INFERENCE_READ,
        Permission.ANALYTICS_READ,
    }
}


def get_permissions_for_role(role: UserRole) -> Set[Permission]:
    """Récupérer toutes les permissions pour un rôle donné"""
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: UserRole, permission: Permission) -> bool:
    """Vérifier si un rôle possède une permission spécifique"""
    return permission in get_permissions_for_role(role)


def can_promote_to_role(promoter_role: UserRole, target_role: UserRole) -> bool:
    """
    Vérifier si un utilisateur peut promouvoir vers un rôle
    Règles :
    - ADMIN peut promouvoir vers tous les rôles
    - CHEF_OPERATOR ne peut pas promouvoir (seulement Admin)
    - OPERATOR ne peut pas promouvoir
    """
    if promoter_role == UserRole.ADMIN:
        return True
    return False


def get_role_hierarchy() -> List[UserRole]:
    """Retourner la hiérarchie des rôles (du plus haut au plus bas)"""
    return [
        UserRole.ADMIN,
        UserRole.CHEF_OPERATOR,
        UserRole.OPERATOR,
        UserRole.VIEWER
    ]


def get_role_display_name(role: UserRole) -> str:
    """Nom d'affichage du rôle en français"""
    display_names = {
        UserRole.ADMIN: "Administrateur",
        UserRole.CHEF_OPERATOR: "Chef Opérateur",
        UserRole.OPERATOR: "Opérateur",
        UserRole.VIEWER: "Observateur"
    }
    return display_names.get(role, role.value)


def get_role_description(role: UserRole) -> str:
    """Description du rôle"""
    descriptions = {
        UserRole.ADMIN: "Tous les droits sur la plateforme. Gestion des utilisateurs, projets, et configuration système.",
        UserRole.CHEF_OPERATOR: "Gestion des projets, équipe, training et déploiement des modèles. Supervision des annotations.",
        UserRole.OPERATOR: "Annotation d'images, exécution d'inférences. Accès limité aux projets assignés.",
        UserRole.VIEWER: "Accès en lecture seule à l'ensemble de la plateforme."
    }
    return descriptions.get(role, "")
