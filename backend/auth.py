"""
Authentication and Authorization Module
JWT token-based authentication with role-based access control
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import os
import secrets
import hashlib

from database import get_db
from models import User, APIKey

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

class AuthManager:
    """Authentication and authorization manager"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def generate_api_key() -> tuple[str, str]:
        """Generate API key and its hash"""
        # Generate random API key
        api_key = f"ak_{secrets.token_urlsafe(32)}"
        
        # Create hash for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Get prefix for identification
        key_prefix = api_key[:12]
        
        return api_key, key_hash, key_prefix
    
    @staticmethod
    def verify_api_key(api_key: str, stored_hash: str) -> bool:
        """Verify API key against stored hash"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return key_hash == stored_hash

# Authentication dependencies

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = AuthManager.verify_token(credentials.credentials)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user

def get_current_user_from_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from API key"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    api_key = credentials.credentials
    
    # Check if it's an API key (starts with 'ak_')
    if not api_key.startswith('ak_'):
        raise credentials_exception
    
    # Find API key in database
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    api_key_obj = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    
    if not api_key_obj or not api_key_obj.is_active:
        raise credentials_exception
    
    # Check expiration
    if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key expired"
        )
    
    # Get user
    user = db.query(User).filter(User.id == api_key_obj.user_id).first()
    if not user or not user.is_active:
        raise credentials_exception
    
    # Update usage statistics
    api_key_obj.usage_count += 1
    api_key_obj.last_used = datetime.utcnow()
    db.commit()
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def get_analyst_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require analyst or admin role"""
    if current_user.role not in ["analyst", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Permission checking
class PermissionChecker:
    """Check user permissions for specific operations"""
    
    @staticmethod
    def can_upload_data(user: User) -> bool:
        """Check if user can upload data"""
        return user.role in ["user", "analyst", "admin"]
    
    @staticmethod
    def can_process_data(user: User) -> bool:
        """Check if user can process data"""
        return user.role in ["user", "analyst", "admin"]
    
    @staticmethod
    def can_create_visualizations(user: User) -> bool:
        """Check if user can create visualizations"""
        return user.role in ["user", "analyst", "admin"]
    
    @staticmethod
    def can_export_data(user: User) -> bool:
        """Check if user can export data"""
        return user.role in ["user", "analyst", "admin"]
    
    @staticmethod
    def can_manage_users(user: User) -> bool:
        """Check if user can manage other users"""
        return user.role == "admin"
    
    @staticmethod
    def can_access_dataset(user: User, dataset_user_id: str) -> bool:
        """Check if user can access specific dataset"""
        return user.role == "admin" or user.id == dataset_user_id
    
    @staticmethod
    def can_delete_dataset(user: User, dataset_user_id: str) -> bool:
        """Check if user can delete specific dataset"""
        return user.role == "admin" or user.id == dataset_user_id

# Rate limiting (simple implementation)
class RateLimiter:
    """Simple rate limiter for API endpoints"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, user_id: str, limit: int = 100, window: int = 3600) -> bool:
        """Check if request is allowed within rate limit"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window)
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[user_id]) >= limit:
            return False
        
        # Add current request
        self.requests[user_id].append(now)
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

def check_rate_limit(
    current_user: User = Depends(get_current_active_user),
    limit: int = 100
):
    """Rate limiting dependency"""
    if not rate_limiter.is_allowed(current_user.id, limit):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

# Utility functions
def get_password_hash(password: str) -> str:
    """Get password hash (convenience function)"""
    return AuthManager.get_password_hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password (convenience function)"""
    return AuthManager.verify_password(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create access token (convenience function)"""
    return AuthManager.create_access_token(data, expires_delta)

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create refresh token (convenience function)"""
    return AuthManager.create_refresh_token(data)