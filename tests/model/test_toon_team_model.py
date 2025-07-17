"""
Unit tests for ToonTeam model.
"""

import pytest
from sqlalchemy.orm import Session
from app.models.toon_team import ToonTeam
from app.models.toon import Toon
from app.models.team import Team
from app.models.member import Member
from app.models.guild import Guild
from app.models.user import User
from app.utils.password import hash_password


class TestToonTeamModel:
    def test_create_toon_team(self, db_session: Session):
        """Test creating a ToonTeam relationship."""
        # Create required dependencies
        user = User(
            username="testuser",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add(guild)
        db_session.commit()

        member = Member(
            display_name="Test Member",
            guild_id=guild.id,
        )
        db_session.add(member)
        db_session.commit()

        team = Team(
            name="Test Team",
            guild_id=guild.id,
            created_by=user.id,
        )
        db_session.add(team)
        db_session.commit()

        toon = Toon(
            member_id=member.id,
            username="TestToon",
            class_="Warrior",
            role="Tank",
            is_main=True,  # type: ignore[assignment]
        )
        db_session.add(toon)
        db_session.commit()

        # Create ToonTeam relationship
        toon_team = ToonTeam(
            toon_id=toon.id,
            team_id=team.id,
        )
        db_session.add(toon_team)
        db_session.commit()

        # Verify the relationship was created
        assert toon_team.id is not None
        assert toon_team.toon_id == toon.id
        assert toon_team.team_id == team.id
        assert toon_team.created_at is not None
        assert toon_team.updated_at is not None

    def test_toon_team_relationships(self, db_session: Session):
        """Test that ToonTeam relationships work correctly."""
        # Create required dependencies
        user = User(
            username="testuser",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add(guild)
        db_session.commit()

        member = Member(
            display_name="Test Member",
            guild_id=guild.id,
        )
        db_session.add(member)
        db_session.commit()

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

        toon = Toon(
            member_id=member.id,
            username="TestToon",
            class_="Warrior",
            role="Tank",
            is_main=True,  # type: ignore[assignment]
        )
        db_session.add(toon)
        db_session.commit()

        # Create ToonTeam relationships
        toon_team1 = ToonTeam(toon_id=toon.id, team_id=team1.id)
        toon_team2 = ToonTeam(toon_id=toon.id, team_id=team2.id)
        db_session.add_all([toon_team1, toon_team2])
        db_session.commit()

        # Test relationships
        assert toon_team1.toon_id == toon.id
        assert toon_team1.team_id == team1.id
        assert toon_team2.toon_id == toon.id
        assert toon_team2.team_id == team2.id

        # Test that toon can access teams through relationship
        db_session.refresh(toon)
        assert len(toon.teams) == 2
        assert team1 in toon.teams
        assert team2 in toon.teams

        # Test that team can access toons through relationship
        db_session.refresh(team1)
        assert len(team1.toons) == 1
        assert toon in team1.toons

    def test_toon_team_cascade_delete(self, db_session: Session):
        """Test that ToonTeam records are deleted when toon is deleted."""
        # Create required dependencies
        user = User(
            username="testuser",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add(guild)
        db_session.commit()

        member = Member(
            display_name="Test Member",
            guild_id=guild.id,
        )
        db_session.add(member)
        db_session.commit()

        team = Team(
            name="Test Team",
            guild_id=guild.id,
            created_by=user.id,
        )
        db_session.add(team)
        db_session.commit()

        toon = Toon(
            member_id=member.id,
            username="TestToon",
            class_="Warrior",
            role="Tank",
            is_main=True,  # type: ignore[assignment]
        )
        db_session.add(toon)
        db_session.commit()

        # Create ToonTeam relationship
        toon_team = ToonTeam(toon_id=toon.id, team_id=team.id)
        db_session.add(toon_team)
        db_session.commit()

        # Verify relationship exists
        assert (
            db_session.query(ToonTeam).filter_by(toon_id=toon.id).first()
            is not None
        )

        # Delete the toon
        db_session.delete(toon)
        db_session.commit()

        # Verify ToonTeam record was also deleted
        assert (
            db_session.query(ToonTeam).filter_by(toon_id=toon.id).first()
            is None
        )
