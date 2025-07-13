#!/usr/bin/env python3
"""
Script to create the first superuser with proper password hashing.

This script creates a superuser account that can be used to manage the application.
The password is properly hashed using bcrypt before being stored in the database.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models.user import User
from app.models.token import Token
from app.utils.password import hash_password
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_superuser(username: str, password: str, db: Session) -> User:
    """
    Create a superuser with the given credentials.

    Args:
        username: Username for the superuser
        password: Plain text password (will be hashed)
        db: Database session

    Returns:
        Created User object

    Raises:
        ValueError: If username already exists or password is invalid
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise ValueError(f"User '{username}' already exists")

    # Hash the password
    hashed_password = hash_password(password)

    # Create superuser
    user = User(
        username=username,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"Superuser '{username}' created successfully")
    return user


def create_superuser_token(user: User, db: Session) -> Token:
    """
    Create a token for the superuser.

    Args:
        user: The superuser
        db: Database session

    Returns:
        Created Token object
    """
    token = Token.create_user_token(
        user_id=user.id, name="Superuser Token"  # type: ignore[arg-type]
    )

    db.add(token)
    db.commit()
    db.refresh(token)

    logger.info(f"Token created for superuser '{user.username}'")
    return token


def main():
    """Main function to create a superuser interactively."""
    print("=== GuildRoster Superuser Creation ===")
    print()

    # Get username
    username = input("Enter username for superuser: ").strip()
    if not username:
        print("Error: Username cannot be empty")
        sys.exit(1)

    # Get password
    password = input("Enter password for superuser: ")
    if not password:
        print("Error: Password cannot be empty")
        sys.exit(1)

    # Confirm password
    confirm_password = input("Confirm password: ")
    if password != confirm_password:
        print("Error: Passwords do not match")
        sys.exit(1)

    # Validate password strength
    if len(password) < 8:
        print("Error: Password must be at least 8 characters long")
        sys.exit(1)

    try:
        # Get database session
        db = next(get_db())

        # Create superuser
        user = create_superuser(username, password, db)

        # Create token
        token = create_superuser_token(user, db)

        print()
        print("=== Superuser Created Successfully ===")
        print(f"Username: {user.username}")
        print(f"User ID: {user.id}")
        print(f"Token: {token.key}")
        print()
        print("You can now use this token to authenticate with the API:")
        print(f"Authorization: Bearer {token.key}")
        print()
        print("API endpoints:")
        print("- Interactive docs: http://localhost:8000/docs")
        print("- Health check: http://localhost:8000/")
        print("- Users: http://localhost:8000/users/")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
