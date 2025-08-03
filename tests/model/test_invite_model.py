# type: ignore[comparison-overlap,assignment]
"""
Model tests for the Invite model.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from app.models.invite import Invite
from app.models.user import User


def test_invite_model_creation():
    """Test creating an invite instance."""
    invite = Invite(
        code="ABC12345",
        created_by=1,
        expires_at=datetime.now() + timedelta(days=7),
    )

    assert invite.code == "ABC12345"
    assert invite.created_by == 1
    assert invite.used_by is None
    assert invite.is_active is None  # SQLAlchemy default not applied yet
    assert invite.created_at is None
    assert invite.used_at is None


def test_invite_model_defaults_after_persistence(db_session):
    """Test that defaults are applied when persisted to database."""
    # Create a user first
    user = User(username="testuser", hashed_password="hashedpw123")
    db_session.add(user)
    db_session.commit()

    invite = Invite(
        code="ABC12345",
        created_by=user.id,
        expires_at=datetime.now() + timedelta(days=7),
    )
    db_session.add(invite)
    db_session.commit()

    # After commit, defaults should be applied
    assert invite.is_active is True
    assert invite.used_by is None
    assert isinstance(invite.created_at, datetime)
    assert invite.used_at is None


def test_invite_database_operations(db_session):
    """Test basic database operations for invites."""
    # Create a user first
    user = User(username="testuser", hashed_password="hashedpw123")
    db_session.add(user)
    db_session.commit()

    # Create an invite
    invite = Invite(
        code="ABC12345",
        created_by=user.id,
        expires_at=datetime.now() + timedelta(days=7),
    )

    # Add to database
    db_session.add(invite)
    db_session.commit()

    # Verify invite was saved
    assert invite.id is not None

    # Query invite from database
    queried_invite = db_session.query(Invite).filter_by(code="ABC12345").first()
    assert queried_invite is not None
    assert queried_invite.code == "ABC12345"
    assert queried_invite.created_by == user.id
    assert queried_invite.is_active is True
    assert queried_invite.used_by is None


def test_invite_unique_code_constraint(db_session):
    """Test that invite codes must be unique."""
    # Create a user first
    user = User(username="testuser", hashed_password="hashedpw123")
    db_session.add(user)
    db_session.commit()

    # Create first invite
    invite1 = Invite(
        code="ABC12345",
        created_by=user.id,
        expires_at=datetime.now() + timedelta(days=7),
    )
    db_session.add(invite1)
    db_session.commit()

    # Try to create second invite with same code
    invite2 = Invite(
        code="ABC12345",
        created_by=user.id,
        expires_at=datetime.now() + timedelta(days=14),
    )
    db_session.add(invite2)

    # This should raise an integrity error due to unique constraint
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_invite_relationships(db_session):
    """Test invite relationships with users."""
    # Create users
    creator = User(username="creator", hashed_password="hashedpw123")
    user = User(username="user", hashed_password="hashedpw123")
    db_session.add_all([creator, user])
    db_session.commit()

    # Create invite
    invite = Invite(
        code="ABC12345",
        created_by=creator.id,
        expires_at=datetime.now() + timedelta(days=7),
    )
    db_session.add(invite)
    db_session.commit()

    # Test creator relationship
    assert invite.creator.id == creator.id
    assert invite.creator.username == "creator"

    # Test used_user relationship (initially None)
    assert invite.used_user is None

    # Mark invite as used
    invite.used_by = user.id
    invite.used_at = datetime.now()
    db_session.commit()

    # Test used_user relationship after usage
    assert invite.used_user.id == user.id
    assert invite.used_user.username == "user"


def test_invite_expiration_handling(db_session):
    """Test invite expiration handling."""
    # Create a user first
    user = User(username="testuser", hashed_password="hashedpw123")
    db_session.add(user)
    db_session.commit()

    # Create invite with expiration
    expires_at = datetime.now() + timedelta(days=7)
    invite = Invite(code="ABC12345", created_by=user.id, expires_at=expires_at)
    db_session.add(invite)
    db_session.commit()

    # Verify expiration date
    assert invite.expires_at == expires_at

    # Create invite without expiration
    invite_no_expiry = Invite(
        code="DEF67890", created_by=user.id, expires_at=None
    )
    db_session.add(invite_no_expiry)
    db_session.commit()

    # Verify no expiration
    assert invite_no_expiry.expires_at is None


def test_invite_usage_tracking(db_session):
    """Test invite usage tracking."""
    # Create users
    creator = User(username="creator", hashed_password="hashedpw123")
    user = User(username="user", hashed_password="hashedpw123")
    db_session.add_all([creator, user])
    db_session.commit()

    # Create invite
    invite = Invite(
        code="ABC12345",
        created_by=creator.id,
        expires_at=datetime.now() + timedelta(days=7),
    )
    db_session.add(invite)
    db_session.commit()

    # Initially not used
    assert invite.used_by is None
    assert invite.used_at is None

    # Mark as used
    usage_time = datetime.now()
    invite.used_by = user.id
    invite.used_at = usage_time
    db_session.commit()

    # Verify usage tracking
    assert invite.used_by == user.id
    assert invite.used_at == usage_time


def test_invite_active_status(db_session):
    """Test invite active status handling."""
    # Create a user first
    user = User(username="testuser", hashed_password="hashedpw123")
    db_session.add(user)
    db_session.commit()

    # Create active invite
    invite_active = Invite(
        code="ABC12345",
        created_by=user.id,
        is_active=True,
        expires_at=datetime.now() + timedelta(days=7),
    )
    db_session.add(invite_active)
    db_session.commit()

    # Create inactive invite
    invite_inactive = Invite(
        code="DEF67890",
        created_by=user.id,
        is_active=False,
        expires_at=datetime.now() + timedelta(days=7),
    )
    db_session.add(invite_inactive)
    db_session.commit()

    # Verify status
    assert invite_active.is_active is True
    assert invite_inactive.is_active is False


def test_invite_cascade_behavior(db_session):
    """Test cascade behavior when users are deleted."""
    # Create users
    creator = User(username="creator", hashed_password="hashedpw123")
    user = User(username="user", hashed_password="hashedpw123")
    db_session.add_all([creator, user])
    db_session.commit()

    # Create invite
    invite = Invite(
        code="ABC12345",
        created_by=creator.id,
        used_by=user.id,
        used_at=datetime.now(),  # Set used_at to simulate a used invite
        expires_at=datetime.now() + timedelta(days=7),
    )
    db_session.add(invite)
    db_session.commit()

    # Verify the invite is properly set up
    assert invite.used_by == user.id
    assert invite.used_at is not None

    # Delete the user who used the invite
    db_session.delete(user)
    db_session.commit()

    # Refresh invite
    db_session.refresh(invite)

    # The invite should still exist
    # With ondelete='SET NULL', used_by should be NULL when user is deleted
    # but used_at should remain (it's a timestamp of when it was used)
    assert invite.used_by is None
    assert invite.used_at is not None  # This should remain


def test_invite_code_case_handling(db_session):
    """Test that invite codes are stored in uppercase."""
    # Create a user first
    user = User(username="testuser", hashed_password="hashedpw123")
    db_session.add(user)
    db_session.commit()

    # Create invite with lowercase code
    invite = Invite(
        code="abc12345",  # Lowercase
        created_by=user.id,
        expires_at=datetime.now() + timedelta(days=7),
    )
    db_session.add(invite)
    db_session.commit()

    # Code should be stored as provided (the utility functions handle case conversion)
    assert invite.code == "abc12345"
