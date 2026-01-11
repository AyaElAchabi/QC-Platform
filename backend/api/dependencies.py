"""
FastAPI dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import List, Callable

from core.database import SessionLocal
from models.user import User
from models.roles import UserRole, Permission, has_permission as check_permission

security = HTTPBearer()


def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    try:
        SECRET_KEY = "change-this-to-a-random-secret-key"
        payload = jwt.decode(
            credentials.credentials, 
            SECRET_KEY, 
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


def require_role(allowed_roles: List[UserRole]) -> Callable:
    """
    Décorateur pour vérifier que l'utilisateur a l'un des rôles autorisés
    
    Usage:
        @router.get("/admin-only")
        def admin_endpoint(user: User = Depends(require_role([UserRole.ADMIN]))):
            ...
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


def require_permission(required_permission: Permission) -> Callable:
    """
    Décorateur pour vérifier qu'un utilisateur a une permission spécifique
    
    Usage:
        @router.post("/training/start")
        def start_training(user: User = Depends(require_permission(Permission.TRAINING_START))):
            ...
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_permission.value}"
            )
        return current_user
    return permission_checker


def require_any_permission(required_permissions: List[Permission]) -> Callable:
    """
    Décorateur pour vérifier qu'un utilisateur a AU MOINS UNE des permissions
    
    Usage:
        @router.get("/models")
        def list_models(
            user: User = Depends(require_any_permission([Permission.MODEL_READ, Permission.TRAINING_READ]))
        ):
            ...
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        has_any = any(current_user.has_permission(perm) for perm in required_permissions)
        if not has_any:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required one of: {[p.value for p in required_permissions]}"
            )
        return current_user
    return permission_checker


def require_all_permissions(required_permissions: List[Permission]) -> Callable:
    """
    Décorateur pour vérifier qu'un utilisateur a TOUTES les permissions
    
    Usage:
        @router.delete("/user/{user_id}")
        def delete_user(
            user: User = Depends(require_all_permissions([Permission.USER_DELETE, Permission.USER_READ]))
        ):
            ...
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        has_all = all(current_user.has_permission(perm) for perm in required_permissions)
        if not has_all:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required all of: {[p.value for p in required_permissions]}"
            )
        return current_user
    return permission_checker


# Helpers pour les cas d'usage courants
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Requiert le rôle ADMIN"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_chef_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Requiert le rôle CHEF_OPERATOR ou ADMIN"""
    if current_user.role not in [UserRole.ADMIN, UserRole.CHEF_OPERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chef Operator or Admin access required"
        )
    return current_user
