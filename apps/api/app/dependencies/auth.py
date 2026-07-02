"""
Authentication Dependencies

Dependency injection for authentication.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[User]:
    """
    Get the current authenticated user.
    This is a placeholder implementation.
    """
    # This is a placeholder - implement actual authentication logic
    token = credentials.credentials
    
    # For testing purposes, return a dummy user
    return User(
        id=1,
        email="test@example.com",
        username="testuser",
        is_active=True
    )

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active user."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return current_user
