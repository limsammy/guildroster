"""
Password hashing utilities using modern Python libraries.

This module provides secure password hashing and verification using industry-standard
algorithms without relying on deprecated modules.
"""

import hashlib
import secrets
import base64
from typing import Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Configuration
SALT_LENGTH = 32
HASH_ALGORITHM = "sha256"
ITERATIONS = 100000  # PBKDF2 iterations


def generate_salt() -> str:
    """Generate a cryptographically secure salt."""
    return secrets.token_urlsafe(SALT_LENGTH)


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2 with SHA256.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string in format: algorithm$iterations$salt$hash

    Raises:
        ValueError: If password is empty or None
    """
    if not password:
        raise ValueError("Password cannot be empty")

    logger.debug("Hashing password")

    # Generate salt
    salt = generate_salt()

    # Hash password using PBKDF2
    hash_obj = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM,
        password.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS,
    )

    # Encode hash as base64
    hash_b64 = base64.b64encode(hash_obj).decode("utf-8")

    # Return in format: algorithm$iterations$salt$hash
    return f"{HASH_ALGORITHM}${ITERATIONS}${salt}${hash_b64}"


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

    try:
        # Parse the hashed password
        parts = hashed_password.split("$")
        if len(parts) != 4:
            return False

        algorithm, iterations_str, salt, stored_hash = parts

        # Validate algorithm
        if algorithm != HASH_ALGORITHM:
            return False

        # Parse iterations
        try:
            iterations = int(iterations_str)
        except ValueError:
            return False

        # Hash the provided password with the same salt and iterations
        hash_obj = hashlib.pbkdf2_hmac(
            algorithm,
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )

        # Encode as base64
        hash_b64 = base64.b64encode(hash_obj).decode("utf-8")

        # Compare hashes
        return secrets.compare_digest(stored_hash, hash_b64)

    except Exception as e:
        logger.warning(f"Error verifying password: {e}")
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a password hash needs to be rehashed (e.g., due to algorithm updates).

    Args:
        hashed_password: The hashed password to check

    Returns:
        True if the hash should be rehashed, False otherwise
    """
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4:
            return True

        algorithm, iterations_str, _, _ = parts

        # Check if algorithm or iterations have changed
        if algorithm != HASH_ALGORITHM:
            return True

        try:
            iterations = int(iterations_str)
            if iterations != ITERATIONS:
                return True
        except ValueError:
            return True

        return False

    except Exception:
        return True


def get_password_hash_info(hashed_password: str) -> dict:
    """
    Get information about a hashed password (for debugging/logging).

    Args:
        hashed_password: The hashed password string

    Returns:
        Dictionary with hash information
    """
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4:
            return {
                "algorithm": "unknown",
                "iterations": 0,
                "salt_length": 0,
                "hash_length": len(hashed_password),
                "is_valid": False,
                "error": "Invalid format",
            }

        algorithm, iterations_str, salt, stored_hash = parts

        try:
            iterations = int(iterations_str)
        except ValueError:
            iterations = 0

        return {
            "algorithm": algorithm,
            "iterations": iterations,
            "salt_length": len(salt),
            "hash_length": len(stored_hash),
            "is_valid": algorithm == HASH_ALGORITHM
            and iterations == ITERATIONS,
        }

    except Exception as e:
        logger.warning(f"Error getting hash info: {e}")
        return {
            "algorithm": "unknown",
            "iterations": 0,
            "salt_length": 0,
            "hash_length": len(hashed_password),
            "is_valid": False,
            "error": str(e),
        }
