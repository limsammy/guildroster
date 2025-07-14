# type: ignore[comparison-overlap,assignment,arg-type]
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team
from app.models.member import Member
from app.models.token import Token
from app.utils.password import hash_password


class TestMemberAPI:
    def _create_superuser(self, db_session: Session):
        user = User(
            username="superuser",
            hashed_password=hash_password("superpassword123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()
        token = Token.create_user_token(user.id, "Superuser Token")
        db_session.add(token)
        db_session.commit()
        return user, token.key

    def _create_regular_user(self, db_session: Session):
        user = User(
            username="regularuser",
            hashed_password=hash_password("userpassword123"),
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()
        token = Token.create_user_token(user.id, "User Token")
        db_session.add(token)
        db_session.commit()
        return user, token.key

    def _create_guild(
        self, db_session: Session, user_id: int, name: str = "Test Guild"
    ):
        guild = Guild(name=name, created_by=user_id)
        db_session.add(guild)
        db_session.commit()
        return guild

    def _create_team(
        self,
        db_session: Session,
        guild_id: int,
        user_id: int,
        name: str = "Test Team",
    ):
        team = Team(name=name, guild_id=guild_id, created_by=user_id)
        db_session.add(team)
        db_session.commit()
        return team

    def test_create_member_superuser(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)
        team = self._create_team(db_session, guild.id, superuser.id)

        # Store IDs in local variables to avoid DetachedInstanceError
        guild_id = guild.id
        team_id = team.id

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "display_name": "Test Member",
            "rank": "Officer",
            "guild_id": guild_id,
            "team_id": team_id,
            "join_date": datetime.now().isoformat(),
        }
        response = client.post("/members/", json=data, headers=headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp["display_name"] == "Test Member"
        assert resp["rank"] == "Officer"
        assert resp["guild_id"] == guild_id
        assert resp["team_id"] == team_id
        assert resp["is_active"] is True

    def test_create_member_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        regular_user, token_key = self._create_regular_user(db_session)
        guild = self._create_guild(db_session, regular_user.id)
        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "display_name": "Test Member",
            "guild_id": guild.id,
        }
        response = client.post("/members/", json=data, headers=headers)
        assert response.status_code == 403

    def test_create_member_duplicate_display_name(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)
        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "display_name": "Test Member",
            "guild_id": guild.id,
        }
        # Create first member
        response1 = client.post("/members/", json=data, headers=headers)
        assert response1.status_code == 201
        # Try to create duplicate
        response2 = client.post("/members/", json=data, headers=headers)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]

    def test_create_member_team_wrong_guild(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        guild1 = self._create_guild(db_session, superuser.id, name="Guild 1")
        guild2 = self._create_guild(db_session, superuser.id, name="Guild 2")
        team = self._create_team(db_session, guild2.id, superuser.id)

        # Store IDs in local variables to avoid DetachedInstanceError
        guild1_id = guild1.id
        team_id = team.id

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "display_name": "Test Member",
            "guild_id": guild1_id,
            "team_id": team_id,
        }
        response = client.post("/members/", json=data, headers=headers)
        assert response.status_code == 400
        assert "Team does not belong" in response.json()["detail"]

    def test_list_members(self, client: TestClient, db_session: Session):
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)
        team = self._create_team(db_session, guild.id, superuser.id)

        # Store IDs in local variables to avoid DetachedInstanceError
        guild_id = guild.id
        team_id = team.id

        # Add members
        member1 = Member(
            display_name="Member 1", guild_id=guild_id, team_id=team_id
        )
        member2 = Member(display_name="Member 2", guild_id=guild_id)
        db_session.add_all([member1, member2])
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/members/", headers=headers)
        assert response.status_code == 200
        members = response.json()
        assert len(members) >= 2

    def test_list_members_filter_by_guild(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        guild1 = self._create_guild(db_session, superuser.id, name="Guild 1")
        guild2 = self._create_guild(db_session, superuser.id, name="Guild 2")

        # Store IDs in local variables to avoid DetachedInstanceError
        guild1_id = guild1.id
        guild2_id = guild2.id

        member1 = Member(display_name="Member 1", guild_id=guild1_id)
        member2 = Member(display_name="Member 2", guild_id=guild2_id)
        db_session.add_all([member1, member2])
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(
            f"/members/?guild_id={guild1_id}", headers=headers
        )
        assert response.status_code == 200
        members = response.json()
        assert all(m["guild_id"] == guild1_id for m in members)

    def test_list_members_filter_by_team(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)
        team1 = self._create_team(
            db_session, guild.id, superuser.id, name="Team 1"
        )
        team2 = self._create_team(
            db_session, guild.id, superuser.id, name="Team 2"
        )

        # Store IDs in local variables to avoid DetachedInstanceError
        guild_id = guild.id
        team1_id = team1.id
        team2_id = team2.id

        member1 = Member(
            display_name="Member 1", guild_id=guild_id, team_id=team1_id
        )
        member2 = Member(
            display_name="Member 2", guild_id=guild_id, team_id=team2_id
        )
        db_session.add_all([member1, member2])
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/members/?team_id={team1_id}", headers=headers)
        assert response.status_code == 200
        members = response.json()
        assert all(m["team_id"] == team1_id for m in members)

    def test_get_member_by_id(self, client: TestClient, db_session: Session):
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)

        # Store ID in local variable to avoid DetachedInstanceError
        guild_id = guild.id

        member = Member(display_name="Test Member", guild_id=guild_id)
        db_session.add(member)
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/members/{member.id}", headers=headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp["id"] == member.id
        assert resp["display_name"] == "Test Member"

    def test_get_member_not_found(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/members/99999", headers=headers)
        assert response.status_code == 404

    def test_get_members_by_guild(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)

        # Store ID in local variable to avoid DetachedInstanceError
        guild_id = guild.id

        member = Member(display_name="GuildMember", guild_id=guild_id)
        db_session.add(member)
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/members/guild/{guild_id}", headers=headers)
        assert response.status_code == 200
        members = response.json()
        assert any(m["display_name"] == "GuildMember" for m in members)

    def test_get_members_by_team(self, client: TestClient, db_session: Session):
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)
        team = self._create_team(db_session, guild.id, superuser.id)

        # Store IDs in local variables to avoid DetachedInstanceError
        guild_id = guild.id
        team_id = team.id

        member = Member(
            display_name="TeamMember", guild_id=guild_id, team_id=team_id
        )
        db_session.add(member)
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/members/team/{team_id}", headers=headers)
        assert response.status_code == 200
        members = response.json()
        assert any(m["display_name"] == "TeamMember" for m in members)

    def test_update_member_superuser(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)

        # Store ID in local variable to avoid DetachedInstanceError
        guild_id = guild.id

        member = Member(display_name="Old Name", guild_id=guild_id)
        db_session.add(member)
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "display_name": "New Name",
            "rank": "Guild Master",
            "is_active": False,
        }
        response = client.put(
            f"/members/{member.id}", json=data, headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert resp["display_name"] == "New Name"
        assert resp["rank"] == "Guild Master"
        assert resp["is_active"] is False

    def test_update_member_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        regular_user, reg_token = self._create_regular_user(db_session)
        guild = self._create_guild(db_session, superuser.id)

        # Store ID in local variable to avoid DetachedInstanceError
        guild_id = guild.id

        member = Member(display_name="Test Member", guild_id=guild_id)
        db_session.add(member)
        db_session.commit()
        headers = {"Authorization": f"Bearer {reg_token}"}
        data = {"display_name": "New Name"}
        response = client.put(
            f"/members/{member.id}", json=data, headers=headers
        )
        assert response.status_code == 403

    def test_update_member_duplicate_display_name(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)
        member1 = Member(display_name="Member1", guild_id=guild.id)
        member2 = Member(display_name="Member2", guild_id=guild.id)
        db_session.add_all([member1, member2])
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"display_name": "Member2"}
        response = client.put(
            f"/members/{member1.id}", json=data, headers=headers
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_delete_member_superuser(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        guild = self._create_guild(db_session, superuser.id)
        member = Member(display_name="DeleteMe", guild_id=guild.id)
        db_session.add(member)
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete(f"/members/{member.id}", headers=headers)
        assert response.status_code == 204
        # Confirm deleted
        response = client.get(f"/members/{member.id}", headers=headers)
        assert response.status_code == 404

    def test_delete_member_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        superuser, token_key = self._create_superuser(db_session)
        regular_user, reg_token = self._create_regular_user(db_session)
        guild = self._create_guild(db_session, superuser.id)
        member = Member(display_name="DeleteMe", guild_id=guild.id)
        db_session.add(member)
        db_session.commit()
        headers = {"Authorization": f"Bearer {reg_token}"}
        response = client.delete(f"/members/{member.id}", headers=headers)
        assert response.status_code == 403
