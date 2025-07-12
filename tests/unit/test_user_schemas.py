import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.user import UserBase, UserResponse, UserListResponse


class TestUserBase:
    def test_valid_user_base(self):
        """Test creating a valid UserBase instance."""
        data = {
            "username": "testuser",
            "is_active": True,
            "is_superuser": False,
        }
        user = UserBase(**data)
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.is_superuser is False

    def test_user_base_missing_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError):
            UserBase(username="testuser")  # Missing is_active and is_superuser

    def test_user_base_invalid_types(self):
        """Test that invalid types raise validation errors."""
        with pytest.raises(ValidationError):
            UserBase(
                username=123,  # Should be string
                is_active="not_boolean",  # Should be boolean
                is_superuser=False,
            )


class TestUserResponse:
    def test_valid_user_response(self):
        """Test creating a valid UserResponse instance."""
        now = datetime.now()
        data = {
            "id": 1,
            "username": "testuser",
            "is_active": True,
            "is_superuser": False,
            "created_at": now,
            "updated_at": now,
        }
        user = UserResponse(**data)
        assert user.id == 1
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.created_at == now
        assert user.updated_at == now

    def test_user_response_from_orm(self):
        """Test creating UserResponse from SQLAlchemy model."""
        from app.models.user import User

        # Create a mock SQLAlchemy user object
        user_model = User(
            id=1,
            username="testuser",
            hashed_password="hashedpw",
            is_active=True,
            is_superuser=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Test conversion using from_orm
        user_response = UserResponse.from_orm(user_model)
        assert user_response.id == 1
        assert user_response.username == "testuser"
        assert user_response.is_active is True
        assert user_response.is_superuser is False

    def test_user_response_missing_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError):
            UserResponse(
                username="testuser",
                is_active=True,
                is_superuser=False,
                # Missing id, created_at, updated_at
            )

    def test_user_response_invalid_id(self):
        """Test that invalid ID raises validation error."""
        now = datetime.now()
        with pytest.raises(ValidationError):
            UserResponse(
                id="not_an_integer",  # Should be int
                username="testuser",
                is_active=True,
                is_superuser=False,
                created_at=now,
                updated_at=now,
            )


class TestUserListResponse:
    def test_valid_user_list_response(self):
        """Test creating a valid UserListResponse instance."""
        now = datetime.now()
        users = [
            UserResponse(
                id=1,
                username="user1",
                is_active=True,
                is_superuser=False,
                created_at=now,
                updated_at=now,
            ),
            UserResponse(
                id=2,
                username="user2",
                is_active=False,
                is_superuser=True,
                created_at=now,
                updated_at=now,
            ),
        ]

        response = UserListResponse(users=users, total=2)
        assert len(response.users) == 2
        assert response.total == 2
        assert response.users[0].username == "user1"
        assert response.users[1].username == "user2"

    def test_user_list_response_empty(self):
        """Test creating UserListResponse with empty user list."""
        response = UserListResponse(users=[], total=0)
        assert len(response.users) == 0
        assert response.total == 0

    def test_user_list_response_missing_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError):
            UserListResponse(users=[])  # Missing total

    def test_user_list_response_invalid_total(self):
        """Test that invalid total raises validation error."""
        now = datetime.now()
        users = [
            UserResponse(
                id=1,
                username="user1",
                is_active=True,
                is_superuser=False,
                created_at=now,
                updated_at=now,
            ),
        ]

        with pytest.raises(ValidationError):
            UserListResponse(
                users=users, total="not_an_integer"  # Should be int
            )

    def test_user_list_response_total_mismatch(self):
        """Test that total can be different from actual user count."""
        now = datetime.now()
        users = [
            UserResponse(
                id=1,
                username="user1",
                is_active=True,
                is_superuser=False,
                created_at=now,
                updated_at=now,
            ),
        ]

        # This should work - total can be different from actual count
        response = UserListResponse(users=users, total=100)
        assert len(response.users) == 1
        assert response.total == 100
