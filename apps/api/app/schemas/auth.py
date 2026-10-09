"""
Authentication Schemas

Pydantic models for authentication and user management.
Includes request/response validation for registration, login, token refresh,
password reset, and email verification.

Phase: API Schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


# ============================================================
# ENUMS
# ============================================================

class UserRole(str, Enum):
    """User roles for authorization."""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
    PREMIUM = "premium"


class AccountStatus(str, Enum):
    """Account status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class TokenType(str, Enum):
    """Types of authentication tokens."""
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class RegisterRequest(BaseModel):
    """
    Request schema for user registration.
    
    Attributes:
    -----------
    email : EmailStr
        User's email address (validated)
    password : str
        User's password (8-128 characters, strength validated)
    username : Optional[str]
        User's chosen username (3-50 characters)
    full_name : Optional[str]
        User's full name
    accept_terms : bool
        Whether the user accepts terms of service
    """
    email: EmailStr = Field(
        ...,
        description="User's email address",
        example="user@example.com"
    )
    
    password: str = Field(
        ...,
        description="User's password (8-128 characters)",
        min_length=8,
        max_length=128,
        example="SecurePass123!"
    )
    
    username: Optional[str] = Field(
        None,
        description="User's chosen username (3-50 characters)",
        min_length=3,
        max_length=50,
        example="johndoe"
    )
    
    full_name: Optional[str] = Field(
        None,
        description="User's full name",
        max_length=100,
        example="John Doe"
    )
    
    accept_terms: bool = Field(
        ...,
        description="Whether the user accepts terms of service",
        example=True
    )
    
    @validator('password')
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        import re
        
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    @validator('username')
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format."""
        if v is None:
            return v
        
        import re
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, dots, and hyphens')
        
        return v
    
    @validator('accept_terms')
    def validate_accept_terms(cls, v: bool) -> bool:
        """Validate terms acceptance."""
        if not v:
            raise ValueError('You must accept the terms of service')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "username": "johndoe",
                "full_name": "John Doe",
                "accept_terms": True
            }
        }
    )


class LoginRequest(BaseModel):
    """
    Request schema for user login.
    
    Attributes:
    -----------
    email : EmailStr
        User's email address
    password : str
        User's password
    remember_me : bool
        Whether to extend session duration
    """
    email: EmailStr = Field(
        ...,
        description="User's email address",
        example="user@example.com"
    )
    
    password: str = Field(
        ...,
        description="User's password",
        example="SecurePass123!"
    )
    
    remember_me: bool = Field(
        default=False,
        description="Whether to extend session duration",
        example=False
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "remember_me": False
            }
        }
    )


class RefreshTokenRequest(BaseModel):
    """
    Request schema for refreshing an access token.
    
    Attributes:
    -----------
    refresh_token : str
        Refresh token to exchange for a new access token
    """
    refresh_token: str = Field(
        ...,
        description="Refresh token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )


class PasswordResetRequest(BaseModel):
    """
    Request schema for requesting a password reset.
    
    Attributes:
    -----------
    email : EmailStr
        User's email address
    """
    email: EmailStr = Field(
        ...,
        description="User's email address",
        example="user@example.com"
    )


class PasswordResetConfirmRequest(BaseModel):
    """
    Request schema for confirming a password reset.
    
    Attributes:
    -----------
    token : str
        Password reset token
    new_password : str
        New password
    """
    token: str = Field(
        ...,
        description="Password reset token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    
    new_password: str = Field(
        ...,
        description="New password",
        min_length=8,
        max_length=128,
        example="NewSecurePass123!"
    )
    
    @validator('new_password')
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        import re
        
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v


class EmailVerificationRequest(BaseModel):
    """
    Request schema for email verification.
    
    Attributes:
    -----------
    token : str
        Email verification token
    """
    token: str = Field(
        ...,
        description="Email verification token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )


# ============================================================
# RESPONSE SCHEMAS
# ============================================================

class UserResponse(BaseModel):
    """
    Response schema for user data.
    
    Attributes:
    -----------
    id : UUID
        User's unique identifier
    email : str
        User's email address
    username : Optional[str]
        User's chosen username
    full_name : Optional[str]
        User's full name
    role : UserRole
        User's role
    account_status : AccountStatus
        User's account status
    is_verified : bool
        Whether email is verified
    created_at : datetime
        Account creation timestamp
    last_login : Optional[datetime]
        Last login timestamp
    """
    id: int = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    # FIX: Make full_name optional
    full_name: Optional[str] = Field(None, description="User's full name")
    
    # Optional fields
    username: Optional[str] = Field(None, description="User's chosen username")
    role: UserRole = Field(default=UserRole.USER, description="User's role")
    account_status: Optional[AccountStatus] = Field(None, description="User's account status")
    is_verified: bool = Field(default=False, description="Whether email is verified")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """
    Response schema for authentication tokens.
    
    Attributes:
    -----------
    access_token : str
        Access token for API authentication
    refresh_token : Optional[str]
        Refresh token for obtaining new access tokens
    token_type : str
        Token type (always "bearer")
    expires_in : int
        Token expiration time in seconds
    user : UserResponse
        User information
    """
    access_token: str = Field(..., description="Access token for API authentication")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "johndoe",
                    "full_name": "John Doe",
                    "role": "user",
                    "account_status": "active",
                    "is_verified": True,
                    "created_at": "2024-01-01T00:00:00Z"
                }
            }
        }
    )


class RefreshTokenResponse(BaseModel):
    """
    Response schema for token refresh.
    
    Attributes:
    -----------
    access_token : str
        New access token
    token_type : str
        Token type (always "bearer")
    expires_in : int
        Token expiration time in seconds
    """
    access_token: str = Field(..., description="New access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class PasswordResetResponse(BaseModel):
    """
    Response schema for password reset requests.
    
    Attributes:
    -----------
    message : str
        Success message
    reset_token : Optional[str]
        Reset token (only returned if not using email delivery)
    """
    message: str = Field(..., description="Success message")
    reset_token: Optional[str] = Field(None, description="Reset token")


class EmailVerificationResponse(BaseModel):
    """
    Response schema for email verification.
    
    Attributes:
    -----------
    message : str
        Success message
    is_verified : bool
        Whether email is now verified
    """
    message: str = Field(..., description="Success message")
    is_verified: bool = Field(..., description="Whether email is now verified")


# ============================================================
# ERROR RESPONSES
# ============================================================

class AuthErrorResponse(BaseModel):
    """
    Response schema for authentication errors.
    
    Attributes:
    -----------
    error : str
        Error code
    message : str
        Error message
    details : Optional[Dict[str, Any]]
        Additional error details
    """
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ValidationErrorResponse(BaseModel):
    """
    Response schema for validation errors.
    
    Attributes:
    -----------
    errors : List[Dict[str, Any]]
        List of validation errors
    """
    errors: List[Dict[str, Any]] = Field(..., description="List of validation errors")


# ============================================================
# AUTHENTICATION HELPERS
# ============================================================

def create_auth_response(
    access_token: str,
    user: Dict[str, Any],
    refresh_token: Optional[str] = None,
    expires_in: int = 3600
) -> TokenResponse:
    """
    Create a standardized authentication response.
    
    Parameters:
    -----------
    access_token : str
        Access token
    user : Dict[str, Any]
        User data
    refresh_token : Optional[str]
        Refresh token
    expires_in : int
        Token expiration in seconds
    
    Returns:
    --------
    TokenResponse: Formatted authentication response
    """
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse(**user)
    )


def create_error_response(
    error: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> AuthErrorResponse:
    """
    Create a standardized error response.
    
    Parameters:
    -----------
    error : str
        Error code
    message : str
        Error message
    details : Optional[Dict[str, Any]]
        Additional error details
    
    Returns:
    --------
    AuthErrorResponse: Formatted error response
    """
    return AuthErrorResponse(
        error=error,
        message=message,
        details=details
    )


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    import json
    
    print("=" * 60)
    print("AUTH SCHEMAS TEST")
    print("=" * 60)
    
    # Test 1: Register request
    print("\n📌 Test 1: Register Request")
    try:
        register = RegisterRequest(
            email="test@example.com",
            password="SecurePass123!",
            username="testuser",
            full_name="Test User",
            accept_terms=True
        )
        print(f"✅ Valid registration: {register.email}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Invalid registration
    print("\n📌 Test 2: Invalid Registration")
    try:
        invalid = RegisterRequest(
            email="invalid-email",
            password="weak",
            username="invalid!@#",
            accept_terms=False
        )
    except Exception as e:
        print(f"❌ Validation error: {e}")
    
    # Test 3: Login request
    print("\n📌 Test 3: Login Request")
    login = LoginRequest(
        email="test@example.com",
        password="SecurePass123!"
    )
    print(f"✅ Login request: {login.email}")
    
    # Test 4: Token response
    print("\n📌 Test 4: Token Response")
    user_data = {
        "id": 1,
        "email": "user@example.com",
        "username": "johndoe",
        "full_name": "John Doe",
        "role": UserRole.USER,
        "account_status": AccountStatus.ACTIVE,
        "is_verified": True,
        "created_at": datetime.now()
    }
    
    response = create_auth_response(
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        user=user_data,
        refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        expires_in=3600
    )
    print(f"✅ Token response created")
    print(f"   User: {response.user.username}")
    print(f"   Expires in: {response.expires_in}s")
    
    # Test 5: Password reset request
    print("\n📌 Test 5: Password Reset Request")
    reset_req = PasswordResetRequest(
        email="user@example.com"
    )
    print(f"✅ Password reset request for: {reset_req.email}")
    
    # Test 6: Json serialization
    print("\n📌 Test 6: JSON Serialization")
    json_data = response.model_dump_json(indent=2)
    print(f"  JSON: {json_data[:200]}...")
    
    print("\n✅ All tests completed!")