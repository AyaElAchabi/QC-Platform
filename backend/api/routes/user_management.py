"""
User management routes (admin/chef operator only)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime

from api.dependencies import (
    get_db,
    get_current_user,
    require_admin,
    require_chef_or_admin,
    require_permission
)
from models.user import User
from models.roles import (
    UserRole,
    Permission,
    get_permissions_for_role,
    can_promote_to_role,
    get_role_display_name,
    get_role_description,
    get_role_hierarchy
)

router = APIRouter(prefix="/api/users", tags=["users"])


# Schemas
class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    role_display: str
    is_active: bool
    email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    id: str
    email: str
    role: str
    role_display: str
    is_active: bool
    created_at: datetime


class RoleUpdateRequest(BaseModel):
    new_role: UserRole


class RoleInfo(BaseModel):
    value: str
    display_name: str
    description: str
    permissions: List[str]


class PermissionsResponse(BaseModel):
    role: str
    permissions: List[str]


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Récupérer les informations de l'utilisateur connecté"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role.value,
        role_display=get_role_display_name(current_user.role),
        is_active=current_user.is_active,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at
    )


@router.get("/me/permissions", response_model=PermissionsResponse)
async def get_current_user_permissions(
    current_user: User = Depends(get_current_user)
):
    """Récupérer les permissions de l'utilisateur connecté"""
    permissions = get_permissions_for_role(current_user.role)
    return PermissionsResponse(
        role=current_user.role.value,
        permissions=[p.value for p in permissions]
    )


@router.get("", response_model=List[UserListResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_READ))
):
    """
    Lister tous les utilisateurs
    Permissions: USER_READ
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    return [
        UserListResponse(
            id=str(user.id),
            email=user.email,
            role=user.role.value,
            role_display=get_role_display_name(user.role),
            is_active=user.is_active,
            created_at=user.created_at
        )
        for user in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_READ))
):
    """
    Récupérer un utilisateur spécifique
    Permissions: USER_READ
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role.value,
        role_display=get_role_display_name(user.role),
        is_active=user.is_active,
        email_verified=user.email_verified,
        created_at=user.created_at
    )


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: str,
    request: RoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_PROMOTE))
):
    """
    Changer le rôle d'un utilisateur (promotion/demotion)
    Permissions: USER_PROMOTE (Admin only)
    
    Règles:
    - Seul un Admin peut changer les rôles
    - On ne peut pas se changer son propre rôle
    - On ne peut pas créer/modifier un autre Admin (protection)
    """
    # Vérifier que l'utilisateur cible existe
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Interdire de modifier son propre rôle
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Cannot change your own role"
        )
    
    # Interdire de créer/modifier un Admin (protection)
    if request.new_role == UserRole.ADMIN and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admins can promote to admin role"
        )
    
    # Vérifier que le promoteur a le droit
    if not can_promote_to_role(current_user.role, request.new_role):
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions to promote to {request.new_role.value}"
        )
    
    # Mettre à jour le rôle
    old_role = target_user.role
    target_user.role = request.new_role
    db.commit()
    
    return {
        "message": "Role updated successfully",
        "user_id": user_id,
        "old_role": old_role.value,
        "new_role": request.new_role.value
    }


@router.put("/{user_id}/activate")
async def activate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_UPDATE))
):
    """
    Activer un utilisateur
    Permissions: USER_UPDATE
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    
    return {"message": "User activated successfully"}


@router.put("/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_UPDATE))
):
    """
    Désactiver un utilisateur
    Permissions: USER_UPDATE
    
    Note: Un utilisateur ne peut pas se désactiver lui-même
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Cannot deactivate yourself"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    
    return {"message": "User deactivated successfully"}


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Supprimer un utilisateur (Admin only)
    
    Note: Un admin ne peut pas se supprimer lui-même
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete yourself"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Interdire de supprimer un autre admin
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete another admin"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}


@router.get("/roles/available", response_model=List[RoleInfo])
async def get_available_roles(
    current_user: User = Depends(get_current_user)
):
    """
    Récupérer la liste des rôles disponibles avec leurs permissions
    """
    roles = get_role_hierarchy()
    
    return [
        RoleInfo(
            value=role.value,
            display_name=get_role_display_name(role),
            description=get_role_description(role),
            permissions=[p.value for p in get_permissions_for_role(role)]
        )
        for role in roles
    ]


@router.get("/{user_id}/can-promote-to/{target_role}")
async def check_can_promote(
    user_id: str,
    target_role: UserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Vérifier si l'utilisateur courant peut promouvoir un utilisateur vers un rôle
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    can_promote = can_promote_to_role(current_user.role, target_role)
    
    return {
        "can_promote": can_promote,
        "promoter_role": current_user.role.value,
        "target_role": target_role.value,
        "target_user_current_role": target_user.role.value
    }
