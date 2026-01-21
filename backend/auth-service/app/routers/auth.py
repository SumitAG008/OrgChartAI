"""
Authentication Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import (
    UserRegister, UserLogin, LoginResponse, User, Token,
    PasswordChange, PasswordResetRequest, PasswordReset
)
from app.services.auth_service import (
    AuthService, create_access_token, create_refresh_token,
    verify_token, get_password_hash
)
from app.config import settings
from datetime import timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    token_data = verify_token(token, settings.SECRET_KEY)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service = AuthService()
    user = await auth_service.get_user_by_id(db, token_data.user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Register a new user"""
    try:
        auth_service = AuthService()
        user = await auth_service.register_user(
            db,
            user_data.email,
            user_data.username,
            user_data.password,
            user_data.full_name
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Login user and return access/refresh tokens"""
    auth_service = AuthService()
    user = await auth_service.authenticate_user(
        db,
        credentials.username,
        credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token()
    
    # Create session
    client_ip = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None
    await auth_service.create_session(
        db,
        user.id,
        refresh_token,
        client_ip,
        user_agent
    )
    
    return LoginResponse(
        user=user,
        tokens=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_token_expires.total_seconds())
        )
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    auth_service = AuthService()
    user_id = await auth_service.verify_refresh_token(db, refresh_token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user = await auth_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,  # Keep same refresh token
        expires_in=int(access_token_expires.total_seconds())
    )

@router.post("/logout")
async def logout(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Logout user by revoking refresh token"""
    auth_service = AuthService()
    await auth_service.revoke_session(db, refresh_token)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    auth_service = AuthService()
    
    # Verify current password
    from sqlalchemy import text
    query = text("SELECT hashed_password FROM users WHERE id = :user_id")
    result = await db.execute(query, {"user_id": current_user.id})
    row = result.fetchone()
    
    from app.services.auth_service import verify_password
    if not row or not verify_password(password_data.current_password, row[0]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    new_hash = get_password_hash(password_data.new_password)
    update_query = text("""
        UPDATE users SET hashed_password = :new_hash WHERE id = :user_id
    """)
    await db.execute(update_query, {"new_hash": new_hash, "user_id": current_user.id})
    await db.commit()
    
    return {"message": "Password changed successfully"}
