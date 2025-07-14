# type: ignore[comparison-overlap,assignment]
from app.models.user import User
from sqlalchemy.orm.attributes import InstrumentedAttribute
from datetime import datetime


def test_user_model_creation():
    # Test creating a user instance
    user = User(username="testuser", hashed_password="hashedpw123")
    assert user.username == "testuser"
    assert user.hashed_password == "hashedpw123"
    # SQLAlchemy defaults are only applied when persisted, so these will be None initially
    assert user.is_active is None
    assert user.is_superuser is None
    assert user.created_at is None
    assert user.updated_at is None


def test_user_model_defaults_after_persistence(db_session):
    # Test that defaults are applied when persisted to database
    user = User(username="testuser3", hashed_password="hashedpw123")
    db_session.add(user)
    db_session.commit()

    # After commit, defaults should be applied
    assert user.is_active is True
    assert user.is_superuser is False
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


def test_user_database_operations(db_session):
    # Create a user
    user = User(username="testuser1", hashed_password="hashedpw123")

    # Add to database
    db_session.add(user)
    db_session.commit()

    # Verify user was saved
    assert user.id is not None

    # Query user from database
    queried_user = (
        db_session.query(User).filter_by(username="testuser1").first()
    )
    assert queried_user is not None
    assert queried_user.username == "testuser1"
    assert queried_user.hashed_password == "hashedpw123"
    assert queried_user.is_active is True
    assert queried_user.is_superuser is False


def test_user_unique_username_constraint(db_session):
    # Create first user
    user1 = User(username="testuser2", hashed_password="hashedpw123")
    db_session.add(user1)
    db_session.commit()

    # Try to create second user with same username
    user2 = User(username="testuser2", hashed_password="differentpw")
    db_session.add(user2)

    # This should raise an integrity error due to unique constraint
    import pytest
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        db_session.commit()
