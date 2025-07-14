import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.member import Member
from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team


class TestMemberModel:
    def test_create_member(self, db_session: Session):
        """Test creating a basic member."""
        # Create required related objects
        user = User(username="testuser", hashed_password="hashed")
        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add_all([user, guild])
        db_session.commit()

        member = Member(
            guild_id=guild.id, display_name="Test Member", rank="Member"
        )
        db_session.add(member)
        db_session.commit()

        assert member.id is not None
        assert member.guild_id == guild.id
        assert member.display_name == "Test Member"
        assert member.rank == "Member"
        assert member.is_active is True  # type: ignore[comparison-overlap]
        assert member.join_date is not None
        assert member.created_at is not None
        assert member.updated_at is not None

    def test_member_relationships(self, db_session: Session):
        """Test member relationships with Guild and Team."""
        # Create required objects
        user = User(username="testuser", hashed_password="hashed")
        guild = Guild(name="Test Guild", created_by=user.id)
        team = Team(name="Test Team", guild_id=guild.id, created_by=user.id)
        db_session.add_all([user, guild, team])
        db_session.commit()

        member = Member(
            guild_id=guild.id, team_id=team.id, display_name="Test Member"
        )
        db_session.add(member)
        db_session.commit()

        # Test relationships
        assert member.guild == guild
        assert member.team == team
        assert member in guild.members
        assert member in team.members

    def test_member_without_team(self, db_session: Session):
        """Test creating a member without team assignment."""
        user = User(username="testuser", hashed_password="hashed")
        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add_all([user, guild])
        db_session.commit()

        member = Member(guild_id=guild.id, display_name="Test Member")
        db_session.add(member)
        db_session.commit()

        assert member.team_id is None
        assert member.team is None  # type: ignore[comparison-overlap]

    def test_member_different_guilds(self, db_session: Session):
        """Test that members can be created in different guilds."""
        user = User(username="testuser", hashed_password="hashed")
        guild1 = Guild(name="Guild 1", created_by=user.id)
        guild2 = Guild(name="Guild 2", created_by=user.id)
        db_session.add_all([user, guild1, guild2])
        db_session.commit()

        member1 = Member(guild_id=guild1.id, display_name="Member in Guild 1")
        member2 = Member(guild_id=guild2.id, display_name="Member in Guild 2")
        db_session.add_all([member1, member2])
        db_session.commit()

        assert member1 in guild1.members
        assert member2 in guild2.members

    def test_member_defaults(self, db_session: Session):
        """Test member default values."""
        user = User(username="testuser", hashed_password="hashed")
        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add_all([user, guild])
        db_session.commit()

        member = Member(guild_id=guild.id, display_name="Test Member")
        db_session.add(member)
        db_session.commit()

        assert member.rank == "Member"
        assert member.is_active is True  # type: ignore[comparison-overlap]
        assert member.team_id is None

    def test_member_guild_foreign_key_constraint(self, db_session: Session):
        """Test guild foreign key constraint."""
        # Try to create member with non-existent guild
        member = Member(guild_id=999, display_name="Test Member")
        db_session.add(member)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_member_team_foreign_key_constraint(self, db_session: Session):
        """Test team foreign key constraint."""
        user = User(username="testuser", hashed_password="hashed")
        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add_all([user, guild])
        db_session.commit()

        # Try to assign non-existent team
        member = Member(
            guild_id=guild.id, team_id=999, display_name="Test Member"
        )
        db_session.add(member)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_member_guild_cascade_deletion(self, db_session: Session):
        """Test cascade deletion when guild is deleted."""
        user = User(username="testuser", hashed_password="hashed")
        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add_all([user, guild])
        db_session.commit()

        member = Member(guild_id=guild.id, display_name="Test Member")
        db_session.add(member)
        db_session.commit()

        member_id = member.id
        db_session.delete(guild)
        db_session.commit()

        # Member should be deleted due to cascade
        deleted_member = (
            db_session.query(Member).filter(Member.id == member_id).first()
        )
        assert deleted_member is None

    def test_member_soft_delete(self, db_session: Session):
        """Test member soft delete functionality."""
        user = User(username="testuser", hashed_password="hashed")
        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add_all([user, guild])
        db_session.commit()

        member = Member(guild_id=guild.id, display_name="Test Member")
        db_session.add(member)
        db_session.commit()

        # Soft delete
        member.is_active = False  # type: ignore[assignment]
        db_session.commit()

        # Member should still exist but be inactive
        assert member.is_active is False  # type: ignore[comparison-overlap]
        assert (
            db_session.query(Member).filter(Member.id == member.id).first()
            is not None
        )

    def test_member_timestamp_updates(self, db_session: Session):
        """Test that updated_at timestamp is updated on changes."""
        user = User(username="testuser", hashed_password="hashed")
        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add_all([user, guild])
        db_session.commit()

        member = Member(guild_id=guild.id, display_name="Test Member")
        db_session.add(member)
        db_session.commit()

        original_updated_at = member.updated_at

        # Update member
        member.display_name = "Updated Name"  # type: ignore[assignment]
        db_session.commit()

        assert member.updated_at > original_updated_at

    def test_member_team_assignment(self, db_session: Session):
        """Test assigning and changing team membership."""
        user = User(username="testuser", hashed_password="hashed")
        guild = Guild(name="Test Guild", created_by=user.id)
        team1 = Team(name="Team 1", guild_id=guild.id, created_by=user.id)
        team2 = Team(name="Team 2", guild_id=guild.id, created_by=user.id)
        db_session.add_all([user, guild, team1, team2])
        db_session.commit()

        member = Member(
            guild_id=guild.id, team_id=team1.id, display_name="Test Member"
        )
        db_session.add(member)
        db_session.commit()

        assert member.team == team1
        assert member in team1.members

        # Change team
        member.team_id = team2.id
        db_session.commit()

        assert member.team == team2
        assert member in team2.members
        assert member not in team1.members

    def test_member_rank_values(self, db_session: Session):
        """Test different rank values."""
        user = User(username="testuser", hashed_password="hashed")
        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add_all([user, guild])
        db_session.commit()

        ranks = ["Guild Master", "Officer", "Member", "Recruit"]

        for rank in ranks:
            member = Member(
                guild_id=guild.id, display_name=f"Member {rank}", rank=rank
            )
            db_session.add(member)
            db_session.commit()

            assert member.rank == rank

    def test_member_display_name_validation(self, db_session: Session):
        """Test display name validation."""
        user = User(username="testuser", hashed_password="hashed")
        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add_all([user, guild])
        db_session.commit()

        # Test empty display name
        member = Member(guild_id=guild.id, display_name="")
        db_session.add(member)

        with pytest.raises(IntegrityError):
            db_session.commit()
