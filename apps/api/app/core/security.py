"""
Security Utilities

Handles password hashing, JWT token creation/validation, and security-related
functionality for authentication and authorization.

Phase: Core Security
"""

from typing import List
import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Union
from enum import Enum
import secrets
import re

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger(__name__)


# ============================================================
# ENUMS
# ============================================================

class TokenType(str, Enum):
    """Types of tokens."""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"
    EMAIL_VERIFICATION = "email_verification"


class TokenStatus(str, Enum):
    """Status of token validation."""
    VALID = "valid"
    EXPIRED = "expired"
    INVALID = "invalid"
    MALFORMED = "malformed"


# ============================================================
# MODELS
# ============================================================

class TokenData(BaseModel):
    """Data contained in a JWT token."""
    user_id: str = Field(..., description="User identifier")
    username: Optional[str] = Field(None, description="Username")
    email: Optional[str] = Field(None, description="Email address")
    token_type: TokenType = Field(default=TokenType.ACCESS, description="Token type")
    scopes: Optional[List[str]] = Field(default=None, description="Token scopes")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")


# ============================================================
# CONFIGURATION
# ============================================================

class SecurityConfig:
    """Security configuration."""

    # JWT Settings.
    # settings.SECRET_KEY is validated at import time: in staging/production
    # Config raises rather than falling back to a public placeholder, so by the
    # time this module is imported the value is guaranteed to be usable there.
    # Outside those environments a development fallback keeps local setup simple.
    _DEV_FALLBACK_SECRET = "dev-only-insecure-secret-do-not-use-in-production"

    SECRET_KEY: str = os.getenv("SECRET_KEY") or settings.SECRET_KEY or _DEV_FALLBACK_SECRET
    ALGORITHM: str = os.getenv("JWT_ALGORITHM") or settings.JWT_ALGORITHM or "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES") or settings.JWT_EXPIRATION_MINUTES or 1440)
    
    # Refresh token settings
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Password settings
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 128
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # Rate limiting
    LOGIN_RATE_LIMIT: int = 5  # attempts
    LOGIN_RATE_WINDOW: int = 300  # seconds
    
    # Token validation
    ALLOW_TOKEN_REFRESH: bool = True
    TOKEN_REFRESH_GRACE_PERIOD: int = 300  # seconds


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Adjust for security vs performance
)


class PasswordValidator:
    """Password validation utilities."""
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength.
        
        Parameters:
        -----------
        password : str
            Password to validate
        
        Returns:
        --------
        tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        config = SecurityConfig()
        
        # Check length
        if len(password) < config.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {config.PASSWORD_MIN_LENGTH} characters long"
        
        if len(password) > config.PASSWORD_MAX_LENGTH:
            return False, f"Password must be less than {config.PASSWORD_MAX_LENGTH} characters long"
        
        # Check for uppercase
        if config.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for lowercase
        if config.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for digit
        if config.PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        # Check for special character
        if config.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        # Check for common passwords
        common_passwords = [
            "password", "123456", "qwerty", "admin", "letmein",
            "welcome", "monkey", "dragon", "master", "hello"
        ]
        if password.lower() in common_passwords:
            return False, "Password is too common. Please choose a stronger password"
        
        return True, None


def hash_password(password: str) -> str:
    """
    Hash a plaintext password.
    
    Parameters:
    -----------
    password : str
        Plaintext password
        
    Returns:
    --------
    str: Hashed password
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise ValueError("Failed to hash password")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Parameters:
    -----------
    plain_password : str
        Plaintext password to verify
    hashed_password : str
        Hashed password to verify against
        
    Returns:
    --------
    bool: True if password matches, False otherwise
    """
    if not plain_password or not hashed_password:
        return False
    
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a password hash needs to be rehashed.
    
    Parameters:
    -----------
    hashed_password : str
        Hashed password to check
        
    Returns:
    --------
    bool: True if needs rehashing, False otherwise
    """
    try:
        return pwd_context.needs_update(hashed_password)
    except Exception:
        return False


def generate_password() -> str:
    """
    Generate a secure random password.
    
    Returns:
    --------
    str: Generated password
    """
    # Generate a password with at least 12 characters
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
    return ''.join(secrets.choice(alphabet) for _ in range(16))


# ============================================================
# JWT TOKEN FUNCTIONS
# ============================================================

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    token_type: TokenType = TokenType.ACCESS
) -> str:
    """
    Create a JWT access token.
    
    Parameters:
    -----------
    data : Dict[str, Any]
        Data to encode in the token (must include 'sub' for user_id)
    expires_delta : Optional[timedelta]
        Custom expiration time
    token_type : TokenType
        Type of token to create
        
    Returns:
    --------
    str: Encoded JWT token
    """
    config = SecurityConfig()
    
    try:
        to_encode = data.copy()
        
        # Ensure required fields
        if 'sub' not in to_encode:
            raise ValueError("Token data must include 'sub' (user_id)")
        
        # Set expiration
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            if token_type == TokenType.REFRESH:
                expire = datetime.now(timezone.utc) + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
            elif token_type == TokenType.RESET_PASSWORD:
                expire = datetime.now(timezone.utc) + timedelta(hours=24)
            elif token_type == TokenType.EMAIL_VERIFICATION:
                expire = datetime.now(timezone.utc) + timedelta(days=7)
            else:
                expire = datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": token_type.value if isinstance(token_type, TokenType) else token_type
        })
        
        # Add token ID for tracking
        if 'jti' not in to_encode:
            to_encode["jti"] = secrets.token_urlsafe(16)
        
        encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
        
        logger.debug(f"Token created for user: {to_encode.get('sub')}, type: {token_type}")
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise ValueError(f"Failed to create token: {str(e)}")


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a refresh token.
    
    Parameters:
    -----------
    data : Dict[str, Any]
        Data to encode in the token
        
    Returns:
    --------
    str: Encoded refresh token
    """
    return create_access_token(data, token_type=TokenType.REFRESH)


def create_password_reset_token(user_id: str, email: str) -> str:
    """
    Create a password reset token.
    
    Parameters:
    -----------
    user_id : str
        User ID
    email : str
        User email
        
    Returns:
    --------
    str: Password reset token
    """
    data = {
        "sub": user_id,
        "email": email,
        "purpose": "password_reset"
    }
    return create_access_token(data, token_type=TokenType.RESET_PASSWORD)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    
    Parameters:
    -----------
    token : str
        JWT token to decode
        
    Returns:
    --------
    Optional[Dict[str, Any]]: Decoded payload or None if invalid
    """
    config = SecurityConfig()
    
    try:
        payload = jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM]
        )
        
        # Check if token is expired
        if 'exp' in payload:
            exp_time = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
            if exp_time < datetime.now(timezone.utc):
                logger.debug("Token has expired")
                return None
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.debug("Token has expired")
        return None
    except jwt.JWTClaimsError:
        logger.debug("Invalid claims in token")
        return None
    except jwt.JWTError as e:
        logger.debug(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        return None


def validate_token(token: str) -> tuple[TokenStatus, Optional[Dict[str, Any]]]:
    """
    Validate a JWT token and return detailed status.
    
    Parameters:
    -----------
    token : str
        JWT token to validate
        
    Returns:
    --------
    tuple[TokenStatus, Optional[Dict[str, Any]]]: (status, payload)
    """
    if not token:
        return TokenStatus.MALFORMED, None
    
    config = SecurityConfig()
    
    try:
        payload = jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM]
        )
        
        # Check expiration
        if 'exp' in payload:
            exp_time = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
            if exp_time < datetime.now(timezone.utc):
                return TokenStatus.EXPIRED, payload
        
        return TokenStatus.VALID, payload
        
    except jwt.ExpiredSignatureError:
        return TokenStatus.EXPIRED, None
    except jwt.JWTError:
        return TokenStatus.INVALID, None
    except Exception:
        return TokenStatus.MALFORMED, None


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from a JWT token.
    
    Parameters:
    -----------
    token : str
        JWT token
        
    Returns:
    --------
    Optional[str]: User ID or None if invalid
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("sub")
    return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get the expiration time of a token.
    
    Parameters:
    -----------
    token : str
        JWT token
        
    Returns:
    --------
    Optional[datetime]: Expiration time or None if invalid
    """
    payload = decode_access_token(token)
    if payload and 'exp' in payload:
        return datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
    return None


def is_token_expired(token: str) -> bool:
    """
    Check if a token is expired.
    
    Parameters:
    -----------
    token : str
        JWT token
        
    Returns:
    --------
    bool: True if expired, False otherwise
    """
    exp = get_token_expiration(token)
    if exp is None:
        return True
    return exp < datetime.now(timezone.utc)


def get_token_type(token: str) -> Optional[TokenType]:
    """
    Get the type of a token.
    
    Parameters:
    -----------
    token : str
        JWT token
        
    Returns:
    --------
    Optional[TokenType]: Token type or None
    """
    payload = decode_access_token(token)
    if payload and 'type' in payload:
        try:
            return TokenType(payload['type'])
        except ValueError:
            return None
    return None


# ============================================================
# TOKEN BLACKLISTING (Optional - requires Redis)
# ============================================================

class TokenBlacklist:
    """Token blacklist for invalidating tokens."""
    
    _blacklisted_tokens = set()
    
    @classmethod
    def add_to_blacklist(cls, token: str) -> None:
        """Add a token to the blacklist."""
        # In production, use Redis with TTL
        # For now, store in memory (cleared on restart)
        if token:
            cls._blacklisted_tokens.add(token)
            logger.debug(f"Token blacklisted: {token[:20]}...")
    
    @classmethod
    def is_blacklisted(cls, token: str) -> bool:
        """Check if a token is blacklisted."""
        return token in cls._blacklisted_tokens
    
    @classmethod
    def clear_blacklist(cls) -> None:
        """Clear the blacklist."""
        cls._blacklisted_tokens.clear()
        logger.info("Token blacklist cleared")


# ============================================================
# SECURE UTILITY FUNCTIONS
# ============================================================

def generate_api_key() -> str:
    """
    Generate a secure API key.
    
    Returns:
    --------
    str: API key
    """
    return f"book_api_{secrets.token_urlsafe(32)}"


def generate_verification_code(length: int = 6) -> str:
    """
    Generate a numeric verification code.
    
    Parameters:
    -----------
    length : int
        Length of the code
        
    Returns:
    --------
    str: Verification code
    """
    return ''.join(secrets.choice('0123456789') for _ in range(length))


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token.
    
    Parameters:
    -----------
    length : int
        Length of the token
        
    Returns:
    --------
    str: Secure token
    """
    return secrets.token_urlsafe(length)


def mask_email(email: str) -> str:
    """
    Mask an email address for privacy.
    
    Parameters:
    -----------
    email : str
        Email address to mask
        
    Returns:
    --------
    str: Masked email
    """
    if not email:
        return ""
    parts = email.split('@')
    if len(parts) != 2:
        return email
    username, domain = parts
    if len(username) <= 2:
        masked_username = username
    else:
        masked_username = username[:2] + '*' * (len(username) - 2)
    return f"{masked_username}@{domain}"


# ============================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================

def get_current_user_id(token: str) -> Optional[str]:
    """
    Get current user ID from token.
    
    Parameters:
    -----------
    token : str
        JWT token
        
    Returns:
    --------
    Optional[str]: User ID or None
    """
    if not token:
        return None
    
    # Check blacklist
    if TokenBlacklist.is_blacklisted(token):
        logger.debug("Token is blacklisted")
        return None
    
    user_id = get_user_id_from_token(token)
    if user_id:
        logger.debug(f"User ID extracted: {user_id}")
    else:
        logger.debug("Invalid token")
    
    return user_id


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SECURITY TEST")
    print("=" * 60)
    
    # Test 1: Password hashing
    print("\n📌 Test 1: Password Hashing")
    password = "SecurePass123!"
    hashed = hash_password(password)
    print(f"  Password: {password}")
    print(f"  Hashed: {hashed[:20]}...")
    print(f"  Verify: {verify_password(password, hashed)}")
    print(f"  Wrong password verify: {verify_password('wrong', hashed)}")
    
    # Test 2: Password validation
    print("\n📌 Test 2: Password Validation")
    validator = PasswordValidator()
    
    test_passwords = [
        ("weak", False),
        ("WeakPass", False),
        ("WeakPass1", True),
        ("WeakPass1!", True),
        ("password123", False),  # Common password
    ]
    
    for pwd, expected in test_passwords:
        is_valid, error = validator.validate_password_strength(pwd)
        print(f"  '{pwd}': {is_valid} {'✅' if is_valid == expected else '❌'}")
        if not is_valid:
            print(f"    Error: {error}")
    
    # Test 3: Token creation
    print("\n📌 Test 3: Token Creation")
    token_data = {
        "sub": "user_123",
        "username": "testuser",
        "email": "test@example.com"
    }
    
    access_token = create_access_token(token_data)
    print(f"  Access token: {access_token[:50]}...")
    
    refresh_token = create_refresh_token(token_data)
    print(f"  Refresh token: {refresh_token[:50]}...")
    
    # Test 4: Token decoding
    print("\n📌 Test 4: Token Decoding")
    decoded = decode_access_token(access_token)
    print(f"  Decoded payload: {decoded}")
    
    # Test 5: Token validation
    print("\n📌 Test 5: Token Validation")
    status, payload = validate_token(access_token)
    print(f"  Token status: {status}")
    if payload:
        print(f"  User ID: {payload.get('sub')}")
        print(f"  Token type: {payload.get('type')}")
    
    # Test 6: Token expiration
    print("\n📌 Test 6: Token Expiration")
    exp = get_token_expiration(access_token)
    print(f"  Expiration: {exp}")
    print(f"  Is expired: {is_token_expired(access_token)}")
    
    # Test 7: User ID extraction
    print("\n📌 Test 7: User ID Extraction")
    user_id = get_user_id_from_token(access_token)
    print(f"  User ID: {user_id}")
    
    # Test 8: Token type
    print("\n📌 Test 8: Token Type")
    token_type = get_token_type(access_token)
    print(f"  Token type: {token_type}")
    
    # Test 9: Password reset token
    print("\n📌 Test 9: Password Reset Token")
    reset_token = create_password_reset_token("user_123", "test@example.com")
    print(f"  Reset token: {reset_token[:50]}...")
    
    # Test 10: Utility functions
    print("\n📌 Test 10: Utility Functions")
    print(f"  API Key: {generate_api_key()}")
    print(f"  Verification Code: {generate_verification_code()}")
    print(f"  Masked Email: {mask_email('testuser@example.com')}")
    
    print("\n✅ All tests completed!")