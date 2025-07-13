"""
Unit tests for Guild model.
"""

import pytest
from sqlalchemy.orm import Session
from app.models.guild import Guild
from app.models.user import User
from app.utils.password import hash_password


class TestGuildModel:
    def test_create_guild(self, db_session: Session):
        """Test creating a guild with valid data."""
        # Create a user first
        user = User(
            username="testuser",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        # Create guild
        guild = Guild(
            name="Test Guild",
            description="A test guild for testing",
            realm="Test Realm",
            faction="Alliance",
            website="https://testguild.com",
            discord="https://discord.gg/testguild",
            created_by=user.id,
        )
        db_session.add(guild)
        db_session.commit()

        assert guild.id is not None
        assert guild.name == "Test Guild"
        assert guild.realm == "Test Realm"
        assert guild.faction == "Alliance"
        assert guild.is_active == True  # type: ignore[comparison-overlap]
        assert guild.created_by == user.id
        assert guild.created_at is not None
        assert guild.updated_at is not None

    def test_guild_relationship_with_user(self, db_session: Session):
        """Test the relationship between guild and user."""
        # Create a user
        user = User(
            username="guildleader",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        # Create guild
        guild = Guild(
            name="Epic Guild",
            description="An epic guild",
            realm="Epic Realm",
            faction="Horde",
            created_by=user.id,
        )
        db_session.add(guild)
        db_session.commit()

        # Test relationship
        assert guild.creator == user
        assert guild in user.created_guilds

    def test_guild_unique_name_constraint(self, db_session: Session):
        """Test that guild names must be unique."""
        # Create a user
        user = User(
            username="testuser",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        # Create first guild
        guild1 = Guild(
            name="Unique Guild",
            realm="Test Realm",
            faction="Alliance",
            created_by=user.id,
        )
        db_session.add(guild1)
        db_session.commit()

        # Try to create second guild with same name
        guild2 = Guild(
            name="Unique Guild",  # Same name
            realm="Different Realm",
            faction="Horde",
            created_by=user.id,
        )
        db_session.add(guild2)

        # This should raise an integrity error
        with pytest.raises(
            Exception
        ):  # SQLAlchemy will raise an integrity error
            db_session.commit()
