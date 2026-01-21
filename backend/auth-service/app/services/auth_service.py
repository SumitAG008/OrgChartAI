"""
Authentication Service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
import secrets
import hashlib
import logging

from app.config import settings
from app.models import User, Token, TokenData

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token() -> str:
    """Create a random refresh token"""
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    """Hash a token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()

def verify_token(token: str, secret_key: str) -> Optional[TokenData]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        if user_id is None:
            return None
        return TokenData(user_id=UUID(user_id), username=username)
    except JWTError:
        return None

class AuthService:
    """Service for authentication operations"""
    
    async def register_user(
        self,
        db: AsyncSession,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None
    ) -> User:
        """Register a new user"""
        # Check if user exists
        query = text("""
            SELECT id FROM users 
            WHERE email = :email OR username = :username
        """)
        result = await db.execute(query, {"email": email, "username": username})
        existing = result.fetchone()
        
        if existing:
            raise ValueError("User with this email or username already exists")
        
        # Create user
        hashed_password = get_password_hash(password)
        insert_query = text("""
            INSERT INTO users (email, username, hashed_password, full_name)
            VALUES (:email, :username, :hashed_password, :full_name)
            RETURNING id, email, username, full_name, is_active, is_superuser, email_verified, created_at, last_login
        """)
        result = await db.execute(
            insert_query,
            {
                "email": email,
                "username": username,
                "hashed_password": hashed_password,
                "full_name": full_name
            }
        )
        await db.commit()
        row = result.fetchone()
        
        # Create default organization for user
        org_query = text("""
            INSERT INTO organizations (name, slug)
            VALUES (:name, :slug)
            RETURNING id
        """)
        org_name = f"{username}'s Organization"
        org_slug = username.lower().replace(" ", "-")
        org_result = await db.execute(
            org_query,
            {"name": org_name, "slug": org_slug}
        )
        org_row = org_result.fetchone()
        org_id = org_row[0]
        
        # Add user as owner
        user_org_query = text("""
            INSERT INTO user_organizations (user_id, organization_id, role)
            VALUES (:user_id, :org_id, 'owner')
        """)
        await db.execute(
            user_org_query,
            {"user_id": row[0], "org_id": org_id}
        )
        await db.commit()
        
        return User(
            id=row[0],
            email=row[1],
            username=row[2],
            full_name=row[3],
            is_active=row[4],
            is_superuser=row[5],
            email_verified=row[6],
            created_at=row[7],
            last_login=row[8]
        )
    
    async def authenticate_user(
        self,
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[User]:
        """Authenticate a user"""
        # Find user by username or email
        query = text("""
            SELECT id, email, username, hashed_password, full_name, 
                   is_active, is_superuser, email_verified, created_at, last_login
            FROM users
            WHERE (username = :identifier OR email = :identifier)
            AND is_active = TRUE
        """)
        result = await db.execute(query, {"identifier": username})
        row = result.fetchone()
        
        if not row:
            return None
        
        # Verify password
        if not verify_password(password, row[3]):  # hashed_password
            return None
        
        # Update last login
        update_query = text("""
            UPDATE users SET last_login = :now WHERE id = :user_id
        """)
        await db.execute(update_query, {"now": datetime.utcnow(), "user_id": row[0]})
        await db.commit()
        
        return User(
            id=row[0],
            email=row[1],
            username=row[2],
            full_name=row[4],
            is_active=row[5],
            is_superuser=row[6],
            email_verified=row[7],
            created_at=row[8],
            last_login=datetime.utcnow()
        )
    
    async def create_session(
        self,
        db: AsyncSession,
        user_id: UUID,
        refresh_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Create a user session with refresh token"""
        token_hash = hash_token(refresh_token)
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        query = text("""
            INSERT INTO user_sessions (user_id, token_hash, expires_at, ip_address, user_agent)
            VALUES (:user_id, :token_hash, :expires_at, :ip_address, :user_agent)
        """)
        await db.execute(
            query,
            {
                "user_id": user_id,
                "token_hash": token_hash,
                "expires_at": expires_at,
                "ip_address": ip_address,
                "user_agent": user_agent
            }
        )
        await db.commit()
    
    async def verify_refresh_token(
        self,
        db: AsyncSession,
        refresh_token: str
    ) -> Optional[UUID]:
        """Verify refresh token and return user_id"""
        token_hash = hash_token(refresh_token)
        
        query = text("""
            SELECT user_id FROM user_sessions
            WHERE token_hash = :token_hash
            AND expires_at > :now
        """)
        result = await db.execute(
            query,
            {"token_hash": token_hash, "now": datetime.utcnow()}
        )
        row = result.fetchone()
        
        if row:
            # Update last_used_at
            update_query = text("""
                UPDATE user_sessions 
                SET last_used_at = :now 
                WHERE token_hash = :token_hash
            """)
            await db.execute(update_query, {"now": datetime.utcnow(), "token_hash": token_hash})
            await db.commit()
            return row[0]
        
        return None
    
    async def revoke_session(
        self,
        db: AsyncSession,
        refresh_token: str
    ) -> None:
        """Revoke a refresh token"""
        token_hash = hash_token(refresh_token)
        query = text("""
            DELETE FROM user_sessions WHERE token_hash = :token_hash
        """)
        await db.execute(query, {"token_hash": token_hash})
        await db.commit()
    
    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Optional[User]:
        """Get user by ID"""
        query = text("""
            SELECT id, email, username, full_name, is_active, is_superuser, 
                   email_verified, created_at, last_login
            FROM users
            WHERE id = :user_id
        """)
        result = await db.execute(query, {"user_id": user_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        return User(
            id=row[0],
            email=row[1],
            username=row[2],
            full_name=row[3],
            is_active=row[4],
            is_superuser=row[5],
            email_verified=row[6],
            created_at=row[7],
            last_login=row[8]
        )
