"""
Authentication API Routes

FastAPI routes for user authentication including registration, login,
token refresh, password reset, and email verification.

Phase: API Routes
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    EmailVerificationRequest,
    AuthErrorResponse,
    create_auth_response,
    create_error_response
)
from app.services.auth_service import (
    AuthService,
    AuthError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
    AccountInactiveError,
    InvalidTokenError,
    TokenExpiredError
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# ERROR HANDLING
# ============================================================

def handle_auth_error(e: Exception) -> HTTPException:
    """
    Handle authentication errors and return appropriate HTTP responses.
    
    Parameters:
    -----------
    e : Exception
        The exception to handle
    
    Returns:
    --------
    HTTPException: Formatted HTTP exception
    """
    if isinstance(e, InvalidCredentialsError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    elif isinstance(e, UserAlreadyExistsError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    elif isinstance(e, UserNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    elif isinstance(e, AccountInactiveError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    elif isinstance(e, InvalidTokenError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    elif isinstance(e, TokenExpiredError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    elif isinstance(e, ValueError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    else:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


# ============================================================
# REGISTRATION
# ============================================================

# Helper function to create consistent responses
def create_auth_response(access_token: str, refresh_token: str, user: dict, expires_in: int = 3600) -> TokenResponse:
    """Create a consistent authentication response."""
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user=user
    )

@router.post(
    "/register",
    response_model=TokenResponse,
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Validation error", "model": AuthErrorResponse},
        409: {"description": "User already exists", "model": AuthErrorResponse}
    },
    summary="Register a new user",
    description="Create a new user account with email and password"
)
async def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Register a new user.
    
    This endpoint creates a new user account and returns access and refresh tokens.
    
    Parameters:
    -----------
    payload : RegisterRequest
        Registration data including email, password, and optional username
    
    Returns:
    --------
    TokenResponse: Authentication tokens and user data
    
    Raises:
    -------
    HTTPException: If registration fails
    """
    try:
        logger.info(f"Registration attempt for email: {payload.email}")
        
        service = AuthService(db)
        user, access_token, refresh_token = service.register(
            email=payload.email,
            password=payload.password,
            username=payload.username,
            full_name=payload.full_name if hasattr(payload, 'full_name') else None
        )
        
        logger.info(f"User registered successfully: {user.email}")
        
        return create_auth_response(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user).model_dump(),
            expires_in=3600
        )#.model_dump()
        
    except Exception as e:
        raise handle_auth_error(e)


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials", "model": AuthErrorResponse},
        403: {"description": "Account inactive", "model": AuthErrorResponse}
    },
    summary="Login user",
    description="Authenticate user and return access and refresh tokens"
)
async def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Login a user.
    
    This endpoint authenticates a user with email and password,
    and returns access and refresh tokens.
    
    Parameters:
    -----------
    payload : LoginRequest
        Login credentials including email and password
    
    Returns:
    --------
    TokenResponse: Authentication tokens and user data
    
    Raises:
    -------
    HTTPException: If login fails
    """
    try:
        logger.info(f"Login attempt for: {payload.email}")
        
        service = AuthService(db)
        user, access_token, refresh_token = service.login(
            email=payload.email,
            password=payload.password,
            remember_me=payload.remember_me if hasattr(payload, 'remember_me') else False
        )
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return create_auth_response(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user).model_dump(),
            expires_in=3600 if not hasattr(payload, 'remember_me') or not payload.remember_me else 2592000  # 30 days
        )#.model_dump()

        logger.debug(f"Response: {response.model_dump()}")

        return response
        
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise handle_auth_error(e)


# ============================================================
# TOKEN REFRESH
# ============================================================

@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid or expired token", "model": AuthErrorResponse}
    },
    summary="Refresh access token",
    description="Get a new access token using a refresh token"
)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Refresh an access token.
    
    This endpoint exchanges a valid refresh token for a new access token.
    
    Parameters:
    -----------
    payload : RefreshTokenRequest
        Refresh token
    
    Returns:
    --------
    TokenResponse: New access token
    
    Raises:
    -------
    HTTPException: If token is invalid or expired
    """
    try:
        service = AuthService(db)
        access_token, expires_in = service.refresh_token(payload.refresh_token)
        
        logger.info("Token refreshed successfully")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in
        ).model_dump()
        
    except Exception as e:
        raise handle_auth_error(e)


# ============================================================
# LOGOUT
# ============================================================

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Logout successful"},
        401: {"description": "Invalid token", "model": AuthErrorResponse}
    },
    summary="Logout user",
    description="Invalidate the current access token"
)
async def logout(
    request: Request,
    db: Session = Depends(get_db)
) -> None:
    """
    Logout a user.
    
    This endpoint invalidates the current access token.
    
    Parameters:
    -----------
    request : Request
        HTTP request containing the authorization header
    
    Raises:
    -------
    HTTPException: If token is invalid
    """
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = auth_header.split(" ")[1]
        
        service = AuthService(db)
        service.logout(token)
        
        logger.info("User logged out")
        
    except Exception as e:
        raise handle_auth_error(e)


# ============================================================
# PASSWORD RESET
# ============================================================

@router.post(
    "/password-reset",
    responses={
        200: {"description": "Password reset email sent"},
        404: {"description": "User not found", "model": AuthErrorResponse}
    },
    summary="Request password reset",
    description="Send password reset email to user"
)
async def request_password_reset(
    payload: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Request a password reset.
    
    This endpoint sends a password reset email to the user.
    
    Parameters:
    -----------
    payload : PasswordResetRequest
        User's email address
    
    Returns:
    --------
    Dict[str, str]: Success message
    
    Raises:
    -------
    HTTPException: If user not found
    """
    try:
        service = AuthService(db)
        reset_token = service.request_password_reset(payload.email)
        
        # In production, send email with reset token
        # For development, return token in response
        
        logger.info(f"Password reset requested for: {payload.email}")
        
        return {
            "message": "Password reset email sent",
            "reset_token": reset_token  # Remove in production
        }
        
    except Exception as e:
        raise handle_auth_error(e)


@router.post(
    "/password-reset/confirm",
    responses={
        200: {"description": "Password reset successful"},
        400: {"description": "Validation error", "model": AuthErrorResponse},
        401: {"description": "Invalid or expired token", "model": AuthErrorResponse}
    },
    summary="Confirm password reset",
    description="Reset password using reset token"
)
async def confirm_password_reset(
    payload: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Confirm a password reset.
    
    This endpoint resets the user's password using a valid reset token.
    
    Parameters:
    -----------
    payload : PasswordResetConfirmRequest
        Reset token and new password
    
    Returns:
    --------
    Dict[str, str]: Success message
    
    Raises:
    -------
    HTTPException: If token is invalid or password validation fails
    """
    try:
        service = AuthService(db)
        service.confirm_password_reset(
            token=payload.token,
            new_password=payload.new_password
        )
        
        logger.info("Password reset confirmed")
        
        return {
            "message": "Password reset successful"
        }
        
    except Exception as e:
        raise handle_auth_error(e)


# ============================================================
# EMAIL VERIFICATION
# ============================================================

@router.post(
    "/verify-email",
    responses={
        200: {"description": "Email verified successfully"},
        401: {"description": "Invalid or expired token", "model": AuthErrorResponse}
    },
    summary="Verify email address",
    description="Verify user's email using verification token"
)
async def verify_email(
    payload: EmailVerificationRequest,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Verify a user's email address.
    
    This endpoint verifies a user's email using a verification token.
    
    Parameters:
    -----------
    payload : EmailVerificationRequest
        Email verification token
    
    Returns:
    --------
    Dict[str, str]: Success message
    
    Raises:
    -------
    HTTPException: If token is invalid or expired
    """
    try:
        service = AuthService(db)
        service.verify_email(payload.token)
        
        logger.info("Email verified successfully")
        
        return {
            "message": "Email verified successfully"
        }
        
    except Exception as e:
        raise handle_auth_error(e)


@router.post(
    "/resend-verification",
    responses={
        200: {"description": "Verification email sent"},
        404: {"description": "User not found", "model": AuthErrorResponse}
    },
    summary="Resend verification email",
    description="Resend email verification link to user"
)
async def resend_verification(
    email: str,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Resend email verification.
    
    This endpoint sends a new verification email to the user.
    
    Parameters:
    -----------
    email : str
        User's email address
    
    Returns:
    --------
    Dict[str, str]: Success message
    
    Raises:
    -------
    HTTPException: If user not found
    """
    try:
        service = AuthService(db)
        user = service.get_user_by_email(email)
        if not user:
            raise UserNotFoundError("User not found")
        
        verification_token = service.send_verification_email(user.id)
        
        logger.info(f"Verification email resent to: {email}")
        
        return {
            "message": "Verification email sent",
            "verification_token": verification_token  # Remove in production
        }
        
    except Exception as e:
        raise handle_auth_error(e)


# ============================================================
# USER STATUS
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        200: {"description": "User data retrieved"},
        401: {"description": "Unauthorized", "model": AuthErrorResponse}
    },
    summary="Get current user",
    description="Get the current authenticated user's data"
)
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current user data.
    
    This endpoint returns the current authenticated user's data.
    
    Parameters:
    -----------
    request : Request
        HTTP request containing the authorization header
    
    Returns:
    --------
    UserResponse: Current user data
    
    Raises:
    -------
    HTTPException: If token is invalid or user not found
    """
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = auth_header.split(" ")[1]
        
        service = AuthService(db)
        user = service.get_current_user(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return UserResponse.model_validate(user).model_dump()
        
    except Exception as e:
        raise handle_auth_error(e)