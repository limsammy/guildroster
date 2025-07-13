"""
Password hashing utilities using passlib and bcrypt.

This module provides secure password hashing and verification using industry-standard
algorithms as recommended in the FastAPI tutorial.
"""

from passlib.context import CryptContext
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Configure password hashing context
# Using bcrypt with default settings (good balance of security vs performance)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against

    Returns:
        True if password matches, False otherwise
    """
    if not plain_password or not hashed_password:
        return False

    logger.debug("Verifying password")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string

    Raises:
        ValueError: If password is empty or None
    """
    if not password:
        raise ValueError("Password cannot be empty")

    logger.debug("Hashing password")
    return pwd_context.hash(password)
