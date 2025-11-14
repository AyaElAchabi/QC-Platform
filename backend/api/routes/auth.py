"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
import bcrypt
import uuid

from api.dependencies import get_db
from models.user import User

router = APIRouter()

# Schemas Pydantic
from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str = "viewer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(user_id, email: str, role: str):
    """Create JWT token"""
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {
        "sub": str(user_id),  # Convert UUID to string
        "email": email,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    SECRET_KEY = "change-this-to-a-random-secret-key"
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")


@router.post("/api/auth/register", status_code=201)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user"""
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        created_at=datetime.utcnow(),
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "role": new_user.role,
        "created_at": new_user.created_at.isoformat(),
    }


@router.post("/api/auth/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get token"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )
    
    # Convert user.id to string to avoid UUID serialization error
    access_token = create_access_token(str(user.id), user.email, user.role)
    
    return {
        "access_token": access_token,
        "refresh_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600
    }
