"""
Authentication Service

Handles user authentication, registration, login, token management,
password reset, and email verification.

Phase: Services
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

# NOTE: AccountStatus is imported from app.schemas.auth below. Importing it
# here as well from app.models.user shadowed that binding (two distinct
# enum classes with the same name).

from app.models.user import User
from app.models.user_profile import UserProfile
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    decode_access_token,
    validate_token,
    get_user_id_from_token,
    TokenStatus,
    TokenType,
    PasswordValidator,
    needs_rehash,
    generate_verification_code,
)
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
    AccountStatus,
    UserRole,
)

logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Base exception for authentication errors."""

    pass


class InvalidCredentialsError(AuthError):
    """Raised when credentials are invalid."""

    pass


class UserNotFoundError(AuthError):
    """Raised when user is not found."""

    pass


class UserAlreadyExistsError(AuthError):
    """Raised when user already exists."""

    pass


class AccountInactiveError(AuthError):
    """Raised when account is inactive."""

    pass


class InvalidTokenError(AuthError):
    """Raised when token is invalid."""

    pass


class TokenExpiredError(AuthError):
    """Raised when token has expired."""

    pass


class AuthService:
    """
    Authentication service for user management.

    Provides registration, login, token management, password reset,
    email verification, and user account management.
    """

    def __init__(self, db: Session):
        """
        Initialize the auth service.

        Parameters:
        -----------
        db : Session
            SQLAlchemy database session
        """
        self.db = db
        self.password_validator = PasswordValidator()

    # ============================================================
    # REGISTRATION
    # ============================================================

    def register(
        self,
        email: str,
        password: str,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        accept_terms: bool = True,
    ) -> Tuple[User, str, Optional[str]]:
        """
        Register a new user.

        Parameters:
        -----------
        email : str
            User's email address
        password : str
            User's password
        username : Optional[str]
            User's chosen username
        full_name : Optional[str]
            User's full name
        accept_terms : bool
            Whether terms are accepted

        Returns:
        --------
        Tuple[User, str, Optional[str]]: (user, access_token, refresh_token)

        Raises:
        -------
        UserAlreadyExistsError: If email already registered
        ValueError: If validation fails
        """
        try:
            # Validate password strength
            is_valid, error_msg = self.password_validator.validate_password_strength(
                password
            )
            if not is_valid:
                raise ValueError(f"Invalid password: {error_msg}")

            # Check if email exists
            existing_email = self.db.query(User).filter(User.email == email).first()

            if existing_email:
                raise UserAlreadyExistsError("Email already registered")

            # Check if username exists (if provided)
            if username:
                existing_username = (
                    self.db.query(User).filter(User.username == username).first()
                )

                if existing_username:
                    raise UserAlreadyExistsError("Username already taken")

            # If no username provided, generate from email
            if not username:
                username = email.split("@")[0]
                # Make sure it's unique
                base_username = username
                counter = 1
                while self.db.query(User).filter(User.username == username).first():
                    username = f"{base_username}{counter}"
                    counter += 1

            # Create user
            user = User(
                email=email,
                username=username,
                full_name=full_name,
                hashed_password=hash_password(password),
                is_active=True,
                is_superuser=False,
                # account_status=AccountStatus.PENDING_VERIFICATION.value
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            # Create the matching profile row.
            #
            # Nothing else creates it: onboarding updates an existing profile
            # and returns [] when absent, while the catalog recommendations
            # service raises ValueError("User profile not found") and the route
            # converts that to HTTP 404. A newly registered user therefore hit
            # "something went wrong" on the dashboard until they completed
            # onboarding. Creating the row here makes every new account
            # immediately usable.
            profile = UserProfile(
                user_id=user.id,
                display_name=full_name or username,
                reading_style="balanced",
                preferred_language="en",
                books_per_year=0,
                total_books_read=0,
                discovery_score=0.5,
                onboarding_completed=False,
                reading_streak_days=0,
                longest_streak_days=0,
                weekly_reading_hours=0.0,
            )
            self.db.add(profile)
            self.db.commit()

            # Generate verification code
            verification_code = generate_verification_code()
            # In production, send verification email here

            # Create tokens
            access_token = create_access_token({"sub": str(user.id)})
            refresh_token = create_refresh_token({"sub": str(user.id)})

            logger.info(f"User registered: {user.email} (ID: {user.id})")

            return user, access_token, refresh_token

        except Exception as e:
            self.db.rollback()
            logger.error(f"Registration error: {e}")
            raise

    # ============================================================
    # LOGIN
    # ============================================================

    def login(
        self, email: str, password: str, remember_me: bool = False
    ) -> Tuple[User, str, Optional[str]]:
        """
        Authenticate a user and generate tokens.

        Parameters:
        -----------
        email : str
            User's email address
        password : str
            User's password
        remember_me : bool
            Whether to extend session duration

        Returns:
        --------
        Tuple[User, str, Optional[str]]: (user, access_token, refresh_token)

        Raises:
        -------
        InvalidCredentialsError: If credentials are invalid
        AccountInactiveError: If account is inactive
        """
        try:
            # Find user by email or username
            user = (
                self.db.query(User)
                .filter(or_(User.email == email, User.username == email))
                .first()
            )

            if not user:
                raise InvalidCredentialsError("Invalid credentials")

            # Check if account is active
            if not user.is_active:
                raise AccountInactiveError("Account is deactivated")

            # Check if account is suspended
            if user.account_status == AccountStatus.SUSPENDED.value:
                raise AccountInactiveError("Account is suspended")

            # Verify password
            if not verify_password(password, user.hashed_password):
                raise InvalidCredentialsError("Invalid credentials")

            # Check if password needs rehash
            if needs_rehash(user.hashed_password):
                user.hashed_password = hash_password(password)
                self.db.commit()

            # Update last login
            user.last_login = datetime.now()
            self.db.commit()

            # Create tokens
            expires_delta = timedelta(days=30) if remember_me else None
            access_token = create_access_token(
                {"sub": str(user.id)}, expires_delta=expires_delta
            )

            refresh_token = create_refresh_token({"sub": str(user.id)})

            logger.info(f"User logged in: {user.email} (ID: {user.id})")

            return user, access_token, refresh_token

        except Exception as e:
            logger.error(f"Login error: {e}")
            raise

    # ============================================================
    # TOKEN MANAGEMENT
    # ============================================================

    def refresh_token(self, refresh_token: str) -> Tuple[str, int]:
        """
        Refresh an access token using a refresh token.

        Parameters:
        -----------
        refresh_token : str
            Refresh token

        Returns:
        --------
        Tuple[str, int]: (new_access_token, expires_in_seconds)

        Raises:
        -------
        InvalidTokenError: If refresh token is invalid
        TokenExpiredError: If refresh token has expired
        """
        try:
            # Validate token
            status, payload = validate_token(refresh_token)

            if status == TokenStatus.EXPIRED:
                raise TokenExpiredError("Refresh token has expired")

            if status != TokenStatus.VALID:
                raise InvalidTokenError("Invalid refresh token")

            # Check token type
            token_type = payload.get("type")
            if token_type != TokenType.REFRESH.value:
                raise InvalidTokenError("Invalid token type")

            # Get user ID
            user_id = payload.get("sub")
            if not user_id:
                raise InvalidTokenError("Invalid token payload")

            # Verify user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError("User not found")

            if not user.is_active:
                raise AccountInactiveError("Account is inactive")

            # Create new access token
            access_token = create_access_token({"sub": str(user.id)})
            expires_in = 3600  # 1 hour

            logger.info(f"Token refreshed for user: {user.email} (ID: {user.id})")

            return access_token, expires_in

        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise

    def validate_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate an access token.

        Parameters:
        -----------
        token : str
            Access token

        Returns:
        --------
        Tuple[bool, Optional[Dict[str, Any]]]: (is_valid, payload)
        """
        status, payload = validate_token(token)

        if status == TokenStatus.VALID:
            # Check if token is blacklisted (optional)
            return True, payload

        return False, None

    def get_current_user(self, token: str) -> Optional[User]:
        """
        Get the current user from a token.

        Parameters:
        -----------
        token : str
            Access token

        Returns:
        --------
        Optional[User]: User or None if invalid
        """
        user_id = get_user_id_from_token(token)
        if not user_id:
            return None

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            return None

        return user

    def logout(self, token: str) -> None:
        """
        Logout a user by invalidating their token.

        Parameters:
        -----------
        token : str
            Access token to invalidate
        """
        # In production, add token to blacklist
        # For now, just log the action
        user_id = get_user_id_from_token(token)
        if user_id:
            logger.info(f"User logged out: {user_id}")

    # ============================================================
    # PASSWORD MANAGEMENT
    # ============================================================

    def request_password_reset(self, email: str) -> str:
        """
        Request a password reset.

        Parameters:
        -----------
        email : str
            User's email address

        Returns:
        --------
        str: Password reset token

        Raises:
        -------
        UserNotFoundError: If user not found
        """
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise UserNotFoundError("User not found")

        token = create_password_reset_token(str(user.id), user.email)

        logger.info(f"Password reset requested for user: {user.email} (ID: {user.id})")

        # In production, send password reset email here

        return token

    def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """
        Confirm a password reset.

        Parameters:
        -----------
        token : str
            Password reset token
        new_password : str
            New password

        Returns:
        --------
        bool: True if successful

        Raises:
        -------
        InvalidTokenError: If token is invalid
        TokenExpiredError: If token has expired
        ValueError: If password validation fails
        """
        try:
            # Validate password
            is_valid, error_msg = self.password_validator.validate_password_strength(
                new_password
            )
            if not is_valid:
                raise ValueError(f"Invalid password: {error_msg}")

            # Validate token
            status, payload = validate_token(token)

            if status == TokenStatus.EXPIRED:
                raise TokenExpiredError("Reset token has expired")

            if status != TokenStatus.VALID:
                raise InvalidTokenError("Invalid reset token")

            # Check token type
            token_type = payload.get("type")
            if token_type != TokenType.RESET_PASSWORD.value:
                raise InvalidTokenError("Invalid token type")

            # Get user ID
            user_id = payload.get("sub")
            if not user_id:
                raise InvalidTokenError("Invalid token payload")

            # Verify user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError("User not found")

            # Update password
            user.hashed_password = hash_password(new_password)
            self.db.commit()

            logger.info(
                f"Password reset confirmed for user: {user.email} (ID: {user.id})"
            )

            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Password reset confirmation error: {e}")
            raise

    # ============================================================
    # EMAIL VERIFICATION
    # ============================================================

    def send_verification_email(self, user_id: UUID) -> str:
        """
        Send email verification to a user.

        Parameters:
        -----------
        user_id : UUID
            User ID

        Returns:
        --------
        str: Verification token

        Raises:
        -------
        UserNotFoundError: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError("User not found")

        # Create verification token
        token = create_access_token(
            {"sub": str(user.id), "email": user.email},
            token_type=TokenType.EMAIL_VERIFICATION,
        )

        logger.info(f"Verification email sent to: {user.email} (ID: {user.id})")

        # In production, send verification email here

        return token

    def verify_email(self, token: str) -> bool:
        """
        Verify a user's email.

        Parameters:
        -----------
        token : str
            Verification token

        Returns:
        --------
        bool: True if verified

        Raises:
        -------
        InvalidTokenError: If token is invalid
        TokenExpiredError: If token has expired
        """
        try:
            # Validate token
            status, payload = validate_token(token)

            if status == TokenStatus.EXPIRED:
                raise TokenExpiredError("Verification token has expired")

            if status != TokenStatus.VALID:
                raise InvalidTokenError("Invalid verification token")

            # Check token type
            token_type = payload.get("type")
            if token_type != TokenType.EMAIL_VERIFICATION.value:
                raise InvalidTokenError("Invalid token type")

            # Get user ID
            user_id = payload.get("sub")
            if not user_id:
                raise InvalidTokenError("Invalid token payload")

            # Verify user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError("User not found")

            # Update user
            user.is_verified = True
            user.account_status = AccountStatus.ACTIVE.value
            self.db.commit()

            logger.info(f"Email verified for user: {user.email} (ID: {user.id})")

            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Email verification error: {e}")
            raise

    # ============================================================
    # USER MANAGEMENT
    # ============================================================

    def get_user(self, user_id: UUID) -> Optional[User]:
        """
        Get a user by ID.

        Parameters:
        -----------
        user_id : UUID
            User ID

        Returns:
        --------
        Optional[User]: User or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.

        Parameters:
        -----------
        email : str
            User's email

        Returns:
        --------
        Optional[User]: User or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.

        Parameters:
        -----------
        username : str
            User's username

        Returns:
        --------
        Optional[User]: User or None if not found
        """
        return self.db.query(User).filter(User.username == username).first()

    def update_user_profile(
        self,
        user_id: UUID,
        full_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> User:
        """
        Update user profile.

        Parameters:
        -----------
        user_id : UUID
            User ID
        full_name : Optional[str]
            New full name
        username : Optional[str]
            New username

        Returns:
        --------
        User: Updated user

        Raises:
        -------
        UserNotFoundError: If user not found
        UserAlreadyExistsError: If username already taken
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError("User not found")

        if full_name is not None:
            user.full_name = full_name

        if username is not None:
            # Check if username exists
            existing = (
                self.db.query(User)
                .filter(User.username == username, User.id != user_id)
                .first()
            )
            if existing:
                raise UserAlreadyExistsError("Username already taken")
            user.username = username

        self.db.commit()
        self.db.refresh(user)

        logger.info(f"User profile updated: {user.email} (ID: {user.id})")

        return user

    def deactivate_user(self, user_id: UUID) -> bool:
        """
        Deactivate a user account.

        Parameters:
        -----------
        user_id : UUID
            User ID

        Returns:
        --------
        bool: True if successful

        Raises:
        -------
        UserNotFoundError: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError("User not found")

        user.is_active = False
        user.account_status = AccountStatus.INACTIVE.value
        self.db.commit()

        logger.info(f"User deactivated: {user.email} (ID: {user.id})")

        return True

    def activate_user(self, user_id: UUID) -> bool:
        """
        Activate a user account.

        Parameters:
        -----------
        user_id : UUID
            User ID

        Returns:
        --------
        bool: True if successful

        Raises:
        -------
        UserNotFoundError: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError("User not found")

        user.is_active = True
        user.account_status = AccountStatus.ACTIVE.value
        self.db.commit()

        logger.info(f"User activated: {user.email} (ID: {user.id})")

        return True

    def delete_user(self, user_id: UUID) -> bool:
        """
        Delete a user account (soft delete).

        Parameters:
        -----------
        user_id : UUID
            User ID

        Returns:
        --------
        bool: True if successful

        Raises:
        -------
        UserNotFoundError: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError("User not found")

        # Soft delete - mark as inactive and remove sensitive data
        user.is_active = False
        user.account_status = AccountStatus.INACTIVE.value
        user.email = f"deleted_{user.id}@deleted.com"
        user.hashed_password = "deleted"
        self.db.commit()

        logger.info(f"User deleted: {user_id}")

        return True


# ============================================================
# FACTORY FUNCTION
# ============================================================


def get_auth_service(db: Session) -> AuthService:
    """
    Factory function for creating AuthService instances.

    Parameters:
    -----------
    db : Session
        Database session

    Returns:
    --------
    AuthService: Auth service instance
    """
    return AuthService(db)


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    from app.core.database import SessionLocal

    print("=" * 60)
    print("AUTH SERVICE TEST")
    print("=" * 60)

    db = SessionLocal()
    service = AuthService(db)

    # Test registration
    print("\n📌 Test 1: Register User")
    try:
        user, access_token, refresh_token = service.register(
            email="test@example.com",
            password="SecurePass123!",
            username="testuser",
            full_name="Test User",
        )
        print(f"✅ User registered: {user.email} (ID: {user.id})")
        print(f"   Access token: {access_token[:50]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test login
    print("\n📌 Test 2: Login")
    try:
        user, access_token, refresh_token = service.login(
            email="test@example.com", password="SecurePass123!"
        )
        print(f"✅ User logged in: {user.email}")
        print(f"   Access token: {access_token[:50]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test get current user
    print("\n📌 Test 3: Get Current User")
    try:
        current_user = service.get_current_user(access_token)
        if current_user:
            print(f"✅ Current user: {current_user.email}")
        else:
            print("❌ User not found")
    except Exception as e:
        print(f"❌ Error: {e}")

    db.close()
    print("\n✅ All tests completed!")
