#!/usr/bin/env python3
"""
Command-line utility to create API tokens for GuildRoster.

Usage:
    python scripts/create_token.py --type system --name "Development Token"
    python scripts/create_token.py --type api --name "Frontend App"
    python scripts/create_token.py --type user --user-id 1 --name "User Token"
"""

import argparse
import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.token import Token
from app.models.user import User


def create_token(
    token_type: str,
    name: str,
    user_id: int = None,
    expires_in_days: int = None,
    db: Session = None,
) -> Token:
    """Create a token and return it."""
    if token_type == "user":
        if not user_id:
            raise ValueError("user_id is required for user tokens")
        token = Token.create_user_token(
            user_id=user_id, name=name, expires_in_days=expires_in_days
        )
    elif token_type == "system":
        token = Token.create_system_token(
            name=name, expires_in_days=expires_in_days
        )
    elif token_type == "api":
        token = Token.create_api_token(
            name=name, expires_in_days=expires_in_days
        )
    else:
        raise ValueError("token_type must be 'user', 'system', or 'api'")

    db.add(token)
    db.commit()
    db.refresh(token)

    return token


def main():
    parser = argparse.ArgumentParser(
        description="Create API tokens for GuildRoster",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a system token for development
  python scripts/create_token.py --type system --name "Development Token"
  
  # Create an API token for frontend
  python scripts/create_token.py --type api --name "Frontend App"
  
  # Create a user token (requires user_id)
  python scripts/create_token.py --type user --user-id 1 --name "User Token"
  
  # Create a token with expiration
  python scripts/create_token.py --type system --name "Temporary Token" --expires 30
        """,
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=["user", "system", "api"],
        help="Type of token to create",
    )

    parser.add_argument(
        "--name", required=True, help="Name/description for the token"
    )

    parser.add_argument(
        "--user-id", type=int, help="User ID (required for user tokens)"
    )

    parser.add_argument(
        "--expires", type=int, help="Expiration in days (optional)"
    )

    args = parser.parse_args()

    # Validate user_id for user tokens
    if args.type == "user" and not args.user_id:
        print("Error: --user-id is required for user tokens", file=sys.stderr)
        sys.exit(1)

    try:
        # Get database session
        db = next(get_db())

        # Validate user exists for user tokens
        if args.type == "user" and args.user_id:
            user = db.query(User).filter(User.id == args.user_id).first()
            if not user:
                print(
                    f"Error: User with ID {args.user_id} not found",
                    file=sys.stderr,
                )
                sys.exit(1)

        # Create the token
        token = create_token(
            token_type=args.type,
            name=args.name,
            user_id=args.user_id,
            expires_in_days=args.expires,
            db=db,
        )

        # Print the result
        print(f"✅ Token created successfully!")
        print(f"Token ID: {token.id}")
        print(f"Token Key: {token.key}")
        print(f"Token Type: {token.token_type}")
        print(f"Name: {token.name}")
        print(f"Active: {token.is_active}")
        if token.expires_at:
            print(f"Expires: {token.expires_at}")
        else:
            print("Expires: Never")

        print(f"\n🔑 Use this token in your requests:")
        print(f"Authorization: Bearer {token.key}")

    except Exception as e:
        print(f"Error creating token: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


if __name__ == "__main__":
    main()
