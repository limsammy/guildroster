# type: ignore[comparison-overlap,assignment]
"""
Unit tests for Team model.
"""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.team import Team
from app.models.guild import Guild
from app.models.user import User
from app.utils.password import hash_password


class TestTeamModel:
    def test_create_team(self, db_session: Session):
        """Test creating a team with valid data."""
        # Create a user first
        user = User(
            username="testuser",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        # Create a guild
        guild = Guild(
            name="Test Guild",
            created_by=user.id,
        )
        db_session.add(guild)
        db_session.commit()

        # Create team
        team = Team(
            name="Raid Team A",
            description="Main raid team",
            guild_id=guild.id,
            created_by=user.id,
        )
        db_session.add(team)
        db_session.commit()

        assert team.id is not None
        assert team.name == "Raid Team A"
        assert team.description == "Main raid team"
        assert team.guild_id == guild.id
        assert team.created_by == user.id
        assert team.is_active is True  # type: ignore[truthy-bool]
        assert team.created_at is not None
        assert team.updated_at is not None

    def test_team_relationships(self, db_session: Session):
        """Test the relationships between team, guild, and user."""
        # Create a user
        user = User(
            username="teamleader",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        # Create a guild
        guild = Guild(
            name="Epic Guild",
            created_by=user.id,
        )
        db_session.add(guild)
        db_session.commit()

        # Create team
        team = Team(
            name="PvP Team",
            description="Competitive PvP team",
            guild_id=guild.id,
            created_by=user.id,
        )
        db_session.add(team)
        db_session.commit()

        # Test relationships
        assert team.guild == guild
        assert team.creator == user
        assert team in guild.teams
        assert team in user.created_teams

    def test_team_unique_name_per_guild(self, db_session: Session):
        """Test that team names must be unique within a guild."""
        # Create a user
        user = User(
            username="testuser",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        # Create a guild
        guild = Guild(
            name="Test Guild",
            created_by=user.id,
        )
        db_session.add(guild)
        db_session.commit()

        # Create first team
        team1 = Team(
            name="Raid Team",
            guild_id=guild.id,
            created_by=user.id,
        )
        db_session.add(team1)
        db_session.commit()

        # Try to create second team with same name in same guild
        team2 = Team(
            name="Raid Team",  # Same name
            guild_id=guild.id,
            created_by=user.id,
        )
        db_session.add(team2)

        # This should raise an integrity error
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_team_names_can_be_same_across_guilds(self, db_session: Session):
        """Test that team names can be the same across different guilds."""
        # Create a user
        user = User(
            username="testuser",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        # Create two guilds
        guild1 = Guild(
            name="Guild 1",
            created_by=user.id,
        )
        guild2 = Guild(
            name="Guild 2",
            created_by=user.id,
        )
        db_session.add_all([guild1, guild2])
        db_session.commit()

        # Create teams with same name in different guilds
        team1 = Team(
            name="Raid Team",
            guild_id=guild1.id,
            created_by=user.id,
        )
        team2 = Team(
            name="Raid Team",  # Same name, different guild
            guild_id=guild2.id,
            created_by=user.id,
        )
        db_session.add_all([team1, team2])
        db_session.commit()

        # Both teams should be created successfully
        assert team1.id is not None
        assert team2.id is not None
        assert team1.name == team2.name
        assert team1.guild_id != team2.guild_id

    def test_team_defaults(self, db_session: Session):
        """Test that team defaults are applied correctly."""
        # Create user and guild
        user = User(
            username="testuser",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        guild = Guild(
            name="Test Guild",
            created_by=user.id,
        )
        db_session.add(guild)
        db_session.commit()

        # Create team without specifying optional fields
        team = Team(
            name="Test Team",
            guild_id=guild.id,
            created_by=user.id,
        )
        db_session.add(team)
        db_session.commit()

        # Check defaults
        assert team.description is None
        assert team.is_active is True  # type: ignore[truthy-bool]
        assert team.created_at is not None
        assert team.updated_at is not None

    def test_team_foreign_key_constraints(self, db_session: Session):
        """Test that foreign key constraints are enforced."""
        # Try to create team with non-existent guild_id
        team = Team(
            name="Test Team",
            guild_id=999,  # Non-existent guild
            created_by=1,  # Non-existent user
        )
        db_session.add(team)

        # This should raise an integrity error
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_team_cascade_delete_from_guild(self, db_session: Session):
        """Test that teams are deleted when their guild is deleted."""
        # Create user and guild
        user = User(
            username="testuser",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        guild = Guild(
            name="Test Guild",
            created_by=user.id,
        )
        db_session.add(guild)
        db_session.commit()

        # Create teams
        team1 = Team(
            name="Team 1",
            guild_id=guild.id,
            created_by=user.id,
        )
        team2 = Team(
            name="Team 2",
            guild_id=guild.id,
            created_by=user.id,
        )
        db_session.add_all([team1, team2])
        db_session.commit()

        # Verify teams exist
        assert db_session.query(Team).count() == 2

        # Delete guild
        db_session.delete(guild)
        db_session.commit()

        # Teams should be deleted due to cascade
        assert db_session.query(Team).count() == 0

    def test_team_soft_delete(self, db_session: Session):
        """Test that teams can be soft deleted using is_active flag."""
        # Create user and guild
        user = User(
            username="testuser",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        guild = Guild(
            name="Test Guild",
            created_by=user.id,
        )
        db_session.add(guild)
        db_session.commit()

        # Create team
        team = Team(
            name="Test Team",
            guild_id=guild.id,
            created_by=user.id,
        )
        db_session.add(team)
        db_session.commit()

        # Soft delete the team
        team.is_active = False  # type: ignore[assignment]
        db_session.commit()

        # Team should still exist in database but be inactive
        assert team.id is not None
        assert team.is_active is False  # type: ignore[truthy-bool]

        # Query should still find the team
        queried_team = db_session.query(Team).filter_by(id=team.id).first()
        assert queried_team is not None
        assert queried_team.is_active is False  # type: ignore[truthy-bool]

    def test_team_update_timestamp(self, db_session: Session):
        """Test that updated_at timestamp is updated when team is modified."""
        # Create user and guild
        user = User(
            username="testuser",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        guild = Guild(
            name="Test Guild",
            created_by=user.id,
        )
        db_session.add(guild)
        db_session.commit()

        # Create team
        team = Team(
            name="Test Team",
            guild_id=guild.id,
            created_by=user.id,
        )
        db_session.add(team)
        db_session.commit()

        original_updated_at = team.updated_at

        # Update team
        team.name = "Updated Team Name"  # type: ignore[assignment]
        db_session.commit()

        # updated_at should be different
        assert team.updated_at > original_updated_at
